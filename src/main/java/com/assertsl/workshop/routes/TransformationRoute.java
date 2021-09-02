package com.assertsl.workshop.routes;

import com.assertsl.workshop.beans.FdaEnricher;
import com.assertsl.workshop.configuration.DatabaseProperties;
import org.apache.camel.Exchange;
import org.apache.camel.LoggingLevel;
import org.apache.camel.builder.RouteBuilder;
import org.apache.camel.http.base.HttpOperationFailedException;
import org.apache.camel.model.dataformat.JsonLibrary;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

@Component
public class TransformationRoute extends RouteBuilder {

    @Autowired
    private DatabaseProperties databaseProperties;

    @Autowired
    private FdaEnricher fdaEnricher;

    @Value("${camel-workshop.uploadDirectory}")
    private String pdfDirectory;

    @Override
    public void configure() throws Exception {

        onException(HttpOperationFailedException.class).handled(true)
                .log(LoggingLevel.ERROR, "error consuming the FDA API: ${exception.message}")
                .log(LoggingLevel.ERROR, "backend response Body: ${exception.responseBody}")
                .setBody(simple("${exception.responseBody}"))
                .unmarshal().json(JsonLibrary.Jackson)
                .setHeader(Exchange.HTTP_RESPONSE_CODE, constant(502)) //BAD GATEWAY
                .end();

        from("direct:getAllDrugs").routeId("getAllDrugsRoute")
                .log("get all drugs")
                .to("jpa:com.assertsl.workshop.domain.DrugStore?query=" + databaseProperties.getGetAllDrugs())
                .end();

        from("direct:getDrug").routeId("getDrugRoute")
                .log("get drug ${headers.ncdCode}")
                .setHeader("CamelJpaParameters", method("transformationBean","getDrugParameters"))
                .to("jpa:com.assertsl.workshop.domain.DrugStore?query=" + databaseProperties.getGetDrug())
                .end();

        from("direct:createDrug").routeId("createDrugRoute")
                .log("creating drug")
                .enrich("direct:getDrugInformation", fdaEnricher)
                .to("jpa:com.assertsl.workshop.domain.DrugStore")
                .end();

        from("direct:updateDrug").routeId("updateDrugRoute")
                .log("updating drug")
                .setHeader("CamelJpaParameters", method("transformationBean","updateDrugParameters"))
                .to("jpa:com.assertsl.workshop.domain.DrugStore?useExecuteUpdate=true&query=" + databaseProperties.getUpdateDrug())
                .end();

        from("direct:disableDrug").routeId("disableDrugRoute")
                .log("disabling drug ${headers.ncdCode}")
                .setHeader("CamelJpaParameters", method("transformationBean","getDrugParameters"))
                .to("jpa:com.assertsl.workshop.domain.DrugStore?query=" + databaseProperties.getGetDrug())
                .bean("transformationBean","disableDrug")
                //TODO: Update the drug with INACTIVE status-----                
                .to("jpa:com.assertsl.workshop.domain.DrugStore")
                .end();


        from("direct:getDrugInformation").routeId("getDrugInformationRoute")
                .log("Getting drug Information from FDA API")
                .setHeader(Exchange.HTTP_QUERY, simple("search=product_ndc:${body.productNdc}"))
                .setHeader(Exchange.HTTP_URI,  constant("https://api.fda.gov/drug/ndc.json"))
                .setHeader(Exchange.HTTP_METHOD, constant("GET"))
                .setBody(constant(null))
                .to("http:invokeFdaApi")
                .log("Response from FDA API ${body}")
                .log("Getting required fields")
                .setHeader("packageDescription", jsonpath("$.results[0].packaging[0].description"))
                .setHeader("labelerName", jsonpath("$.results[0].labeler_name"))
                .setHeader("genericName", jsonpath("$.results[0].generic_name"))
                //TODO: get genericName and labelerName fields----
                .log("Info obtained packageDescription: ${headers.packageDescription}, labelerName: ${headers.labelerName}, genericName: ${headers.genericName}")
                .end();


        from("direct:uploadPdf").routeId("uploadPdfRoute")
                .log("Uploading Pdf File")
                .bean("transformationBean","readContentRequest")
                .to("file:"+ pdfDirectory)
                .setBody(simple("File Upload successfully ${headers.CamelFileName}"))
                .end();

        from("direct:downloadPdf").routeId("downloadPdfRoute")
                .log("Downloading File ${headers.filename}")
                .pollEnrich().simple("file:"+ pdfDirectory + "?fileName=${headers.filename}&noop=true&idempotent=false").timeout(5000)
                .log("sending back to response")
                .end();



    }

}
