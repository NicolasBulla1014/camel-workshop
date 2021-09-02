package com.assertsl.workshop.beans;

import com.assertsl.workshop.domain.DrugStore;
import com.assertsl.workshop.dto.DrugDto;
import org.apache.camel.AggregationStrategy;
import org.apache.camel.Exchange;
import org.springframework.stereotype.Component;

@Component
public class FdaEnricher implements AggregationStrategy {

    @Override
    public Exchange aggregate(Exchange oldExchange, Exchange newExchange) {

        if (newExchange.getIn().getHeader(Exchange.HTTP_RESPONSE_CODE, Integer.class) == 200) {
            DrugDto drugDto = oldExchange.getIn().getBody(DrugDto.class);
            DrugStore drugStore = new DrugStore();

            drugStore.setProductNdc(drugDto.getProductNdc());
            drugStore.setExistences(drugDto.getExistences());
            drugStore.setPrice(drugDto.getPrice());

            //TODO: set fields packageDescription labelerName genericName returned by the query to drugStore---

            drugStore.setPackageDescription(newExchange.getIn().getHeader("packageDescription", String.class));
            drugStore.setLabelerName(newExchange.getIn().getHeader("labelerName", String.class));
            drugStore.setGenericName(newExchange.getIn().getHeader("genericName", String.class));
            newExchange.getIn().setBody(drugStore);
        }
        return newExchange;
    }
}
