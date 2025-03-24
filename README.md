# 🚀 **Spark Scala Project: Data Processing and Analysis Pipeline**

## 🖋️ **Description**
This project leverages **Scala** and **Apache Spark** to automate a comprehensive **data processing pipeline**. The goal is to manipulate, transform, and analyze complex datasets while adhering to a modular structure and data engineering best practices.

---

## ✔️ **Main Objectives**
- **Extraction:** Reading data files in **CSV**, **JSON**, and **XML** formats.
- **Cleaning:** Harmonizing formats and handling missing values.
- **Transformation:** Creating new columns (**Total Price**, **Contract Status**).
- **Analysis:** Aggregating data and generating insights.
- **Validation:** Conducting unit tests using **ScalaTest**.

---

## 💻 **Technologies Used**
- **Scala:** Main programming language.
- **Apache Spark:** Framework for distributed processing.
- **SBT:** Build tool and dependency management.
- **ScalaTest:** Framework for unit testing.
- **Log4j2:** Logging management.

---

## 📂 **Project Structure**
- **main/MainBatch:** Pipeline entry point.
- **args/Args:** Program parameters and arguments.
- **parser/:** Parsing of **JSON**, **CSV**, and **XML** files.
- **reader/:** Data reading classes.
- **traitement/ServiceVente:** Data transformation.
- **test/:** Unit tests with **ScalaTest**.
- **build.sbt:** Dependency configuration.

---

## 📊 **Overview of Analyses**
- Calculation and structuring data by **Contract Status**.
- Aggregation of key metrics (**Average Total Price**, **Number of Contracts**).
- Validation of transformations using test datasets.

