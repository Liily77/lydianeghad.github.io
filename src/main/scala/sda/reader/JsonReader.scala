
package sda.reader

import org.apache.spark.sql.{DataFrame, SparkSession}
case class JsonReader(path: String,
                      multiline: Boolean = true


                    )
  extends Reader {
    val format = "json"

    def read()(implicit  spark: SparkSession): DataFrame = {

        spark.read.format(format)
          .option("multiline", multiline.toString)
          .load(path)

    }
}
