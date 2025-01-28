package sda.traitement

import org.apache.spark.sql.functions._
import org.apache.spark.sql.{DataFrame, SparkSession}
import org.apache.spark.sql.types._

object ServiceVente {

  implicit class DataFrameUtils(dataFrame: DataFrame) {

    def formatter() = {
      // Check if 'HTT_TVA' column exists and split it
      if (dataFrame.columns.contains("HTT_TVA")) {
        dataFrame.withColumn("HTT", split(col("HTT_TVA"), "\\|")(0))
          .withColumn("TVA", split(col("HTT_TVA"), "\\|")(1))
      } else {
        dataFrame
      }
    }

    def createfake(): DataFrame = {
      val res = dataFrame.withColumn("FAKE", lit("fake"))
      res
    }

    def calculTTC(): DataFrame = {
      val dfformatted = formatter()
        .withColumn("HTT", when(col("HTT").isNotNull, regexp_replace(col("HTT"), ",", ".").cast("double")))
        .withColumn("TVA", when(col("TVA").isNotNull, regexp_replace(col("TVA"), ",", ".").cast("double")))

      val dfWithTTC = dfformatted.withColumn(
        "TTC",
        round(col("HTT").cast("double") + (col("HTT").cast("double") * col("TVA").cast("double")), 2)
      )

      val dfFinal = dfWithTTC.drop("HTT", "TVA")
      dfFinal
    }

    def extractDateEndContratVille(): DataFrame = {
      if (dataFrame.schema("MetaData").dataType == StringType) {
        val schema_MetaTransaction = new StructType()
          .add("Ville", StringType, true)
          .add("Date_End_contrat", StringType, true)
          .add("TypeProd", StringType, true)
          .add("produit", ArrayType(StringType, true))

        val schema = new StructType()
          .add("MetaTransaction", ArrayType(schema_MetaTransaction), true)

        dataFrame
          .withColumn("metaJson", from_json(col("MetaData"), schema))
          .withColumn("Ville", col("metaJson.MetaTransaction").getItem(0).getField("Ville"))
          .withColumn("Date_End_contrat", to_date(col("metaJson.MetaTransaction").getItem(0).getField("Date_End_contrat"), "yyyy-MM-dd"))
          .drop("MetaData", "metaJson")
      } else {
        dataFrame
          .withColumn("Ville", col("MetaData.MetaTransaction.Ville"))
          .withColumn("Date_End_contrat", to_date(col("MetaData.MetaTransaction.Date_End_contrat"), "yyyy-MM-dd"))
          .drop("MetaData")
      }
    }

    def contratStatus(): DataFrame = {

      val currentDate = current_date()
      dataFrame.withColumn(
        "Contrat_Status",
        when(col("Date_End_contrat").cast("date") < "2024-01-01", "Expired")
          .otherwise("Active"))


    }

  }
}

