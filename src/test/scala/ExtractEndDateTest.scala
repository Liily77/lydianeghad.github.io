package sda.traitement

import org.apache.spark.sql.SparkSession
import org.scalatest.funsuite.AnyFunSuite

class ExtractEndDateTest extends AnyFunSuite {

  val spark: SparkSession = SparkSession
    .builder
    .appName("Test")
    .config("spark.master", "local")
    .getOrCreate()

  import spark.implicits._
  import ServiceVente._

  test("extractDateEndContratVille extracts Ville and Date_End_contrat correctly") {
    val df = Seq(
      ("1", "100,5|0,19", """{"MetaTransaction":[{"Ville":"Paris","Date_End_contrat":"2024-12-23"},{"TypeProd":"Laitier","produit":["yaourt","laitcoco"]}]}""")
    ).toDF("Id_Client", "HTT_TVA", "MetaData")

    val resultDF = df.extractDateEndContratVille()

    import java.sql.Date
    val expectedDF = Seq(
      ("1", "100,5|0,19", "Paris", Date.valueOf("2024-12-23")) // Ensure DateType for Date_End_contrat
    ).toDF("Id_Client", "HTT_TVA", "Ville", "Date_End_contrat")

    // Debugging output
    println("Result DataFrame:")
    resultDF.show(false)
    resultDF.printSchema()

    println("Expected DataFrame:")
    expectedDF.show(false)
    expectedDF.printSchema()

    // Align columns if necessary
    val alignedResultDF = resultDF.select("Id_Client", "HTT_TVA", "Ville", "Date_End_contrat")
    val alignedExpectedDF = expectedDF.select("Id_Client", "HTT_TVA", "Ville", "Date_End_contrat")

    assert(alignedResultDF.collect() sameElements alignedExpectedDF.collect())
  }

}
