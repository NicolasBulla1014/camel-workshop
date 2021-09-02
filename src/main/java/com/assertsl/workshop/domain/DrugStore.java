package com.assertsl.workshop.domain;

import io.swagger.v3.oas.annotations.Hidden;
import javax.persistence.Entity;
import javax.persistence.Id;
import javax.persistence.Table;
import javax.validation.constraints.NotNull;
import java.math.BigDecimal;

@Entity
@Table(name = "drugs")
public class DrugStore {

    @Id
    @NotNull
    private String productNdc;
    private String genericName;
    private String labelerName;
    private String packageDescription;
    private BigDecimal price;
    private Integer existences;
    private String status = "ACTIVE";

    public String getProductNdc() {
        return productNdc;
    }
    
    public void setProductNdc(String productNdc) {
        this.productNdc = productNdc;
    }

    public String getGenericName() {
        return genericName;
    }

    public void setGenericName(String genericName) {
        this.genericName = genericName;
    }

    public String getLabelerName() {
        return labelerName;
    }

    public void setLabelerName(String labelerName) {
        this.labelerName = labelerName;
    }

    public String getPackageDescription() {
        return packageDescription;
    }

    public void setPackageDescription(String packageDescription) {
        this.packageDescription = packageDescription;
    }

    public BigDecimal getPrice() {
        return price;
    }

    public void setPrice(BigDecimal price) {
        this.price = price;
    }

    public Integer getExistences() {
        return existences;
    }

    public void setExistences(Integer existences) {
        this.existences = existences;
    }

    @Hidden
    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }
}
