
package sda.reader
import org.apache.spark.sql.{DataFrame, SparkSession}
case class XmlReader(path: String,
                     rowTag: String,
                     rootTag: Option[String] = None,
                     charset: Option[String] = Some("UTF-8")
                    ) extends Reader {

  val format = "xml"

  def read()(implicit spark: SparkSession): DataFrame = {
    val reader = spark.read.format(format)
      .option("rowTag", rowTag)
      .option("charset", charset.getOrElse("UTF-8"))


    rootTag.foreach(tag => reader.option("rootTag", tag))

    reader.load(path)
  }
}
