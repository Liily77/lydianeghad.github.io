# 🧠 Neo4j Project: Stored Procedures for Graph Neural Networks 🚀

## 🔄 Context

This project is based on the professor's repository:  
👉 [https://github.com/miyasiffaye/neo4j-cours](https://github.com/miyasiffaye/neo4j-cours)

We cloned this repository to **add `.java` files compiled into `.class`**, corresponding to **Cypher stored procedures** intended for use in Neo4j to build and train a neural network.

## 🎯 Objectives

- Transform initial Python script Cypher queries into **Java stored procedures**.
- Enhance modularity, performance, and reusability of neural network model steps.
- Integrate these procedures into Neo4j for direct execution via the interface or Python scripts.

## 📁 Project Structure

The `.class` files added to the project represent the key stages of neural network training:

- `CreateNetwork.class`, `CreateNeuron.class`, `CreateInputsRowNode.class`, etc.  
  → Creating the network structure (layers, neurons, inputs, outputs)

- `SetInputs.class`, `SetExpectedOutputs.class`  
  → Loading data into Neo4j

- `ForwardPass.class`, `BackwardPassAdam.class`, `ComputeLoss.class`, etc.  
  → Execution of forward pass, loss computation, and backpropagation with Adam optimizer

- `ConstrainWeights.class`  
  → Applying constraints on weights

Each class also includes a `*Result.class` version to manage execution returns.

## 🔧 Technologies Used

- **Neo4j**: Graph-oriented database
- **Java**: Implementation of custom stored procedures
- **Cypher**: Neo4j query language
- **Python**: For the main script (provided by the professor)
- **Git**: Version control and collaboration
- **Maven / Gradle** (optional): Java file compilation

---

## ✅ Completed Steps

- Cloning the base repository
- Implementing Java procedures
- Compiling classes
- Adding `.class` files to the project
- Testing via calls from Neo4j Desktop or Python scripts
