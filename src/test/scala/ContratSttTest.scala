package sda.traitement

import org.apache.spark.sql.{SparkSession, Row}
import org.apache.spark.sql.types._
import org.scalatest.funsuite.AnyFunSuite

class ContratSttTest extends AnyFunSuite {

  val spark: SparkSession = SparkSession
    .builder
    .appName("Test")
    .config("spark.master", "local")
    .getOrCreate()

  import spark.implicits._
  import ServiceVente._

  test("contratStatus assigns correct status based on Date_End_contrat") {
    val df = Seq(
      ("1", "2024-12-23"),
      ("2", "2020-12-23")
    ).toDF("Id_Client", "Date_End_contrat")

    val resultDF = df.contratStatus()

    val expectedSchema = StructType(Array(
      StructField("Id_Client", StringType, true),
      StructField("Date_End_contrat", StringType, true),
      StructField("Contrat_Status", StringType, false)  // Non-nullable
    ))

    val expectedData = spark.sparkContext.parallelize(Seq(
      Row("1", "2024-12-23", "Active"),
      Row("2", "2020-12-23", "Expired")
    ))

    val expectedDF = spark.createDataFrame(expectedData, expectedSchema)

    // Print schemas for debugging
    println("Result DataFrame Schema:")
    resultDF.printSchema()

    println("Expected DataFrame Schema:")
    expectedDF.printSchema()

    // Print data for debugging
    println("Result DataFrame:")
    resultDF.show()

    println("Expected DataFrame:")
    expectedDF.show()

    // Convert DataFrames to sets of tuples for comparison
    val resultSet = resultDF.collect().map(_.toSeq).toSet
    val expectedSet = expectedDF.collect().map(_.toSeq).toSet

    assert(resultSet == expectedSet, "DataFrames are not equal")
  }
}
