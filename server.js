const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");

const app = express();

app.use(cors());
app.use(express.json());

// MongoDB connection
mongoose
  .connect("mongodb://127.0.0.1:27017/portfolioDB")
  .then(() => console.log("MongoDB Connected"))
  .catch((err) => console.log("MongoDB Error:", err));

// Portfolio Schema
const portfolioSchema = new mongoose.Schema({
  bio: {
    type: String,
    required: true
  },

  skills: [
    {
      name: {
        type: String,
        required: true
      }
    }
  ],

  projects: [
    {
      title: {
        type: String,
        required: true
      },
      description: String,
      github: String
    }
  ]
});

const Portfolio = mongoose.model("Portfolio", portfolioSchema);


// CREATE
app.post("/api/portfolio", async (req, res) => {
  try {
    const portfolio = new Portfolio(req.body);

    await portfolio.save();

    res.status(201).json(portfolio);
  } catch (err) {
    res.status(500).json({
      error: err.message
    });
  }
});


// READ ALL
app.get("/api/portfolio", async (req, res) => {
  try {
    const portfolios = await Portfolio.find();

    res.json(portfolios);
  } catch (err) {
    res.status(500).json({
      error: err.message
    });
  }
});


// READ ONE
app.get("/api/portfolio/:id", async (req, res) => {
  try {
    const portfolio = await Portfolio.findById(req.params.id);

    if (!portfolio) {
      return res.status(404).json({
        error: "Portfolio not found"
      });
    }

    res.json(portfolio);
  } catch (err) {
    res.status(500).json({
      error: err.message
    });
  }
});


// UPDATE
app.put("/api/portfolio/:id", async (req, res) => {
  try {
    const updated = await Portfolio.findByIdAndUpdate(
      req.params.id,
      req.body,
      {
        new: true,
        runValidators: true
      }
    );

    if (!updated) {
      return res.status(404).json({
        error: "Portfolio not found"
      });
    }

    res.json(updated);
  } catch (err) {
    res.status(500).json({
      error: err.message
    });
  }
});


// DELETE
app.delete("/api/portfolio/:id", async (req, res) => {
  try {
    const deleted = await Portfolio.findByIdAndDelete(req.params.id);

    if (!deleted) {
      return res.status(404).json({
        error: "Portfolio not found"
      });
    }

    res.json({
      message: "Portfolio deleted successfully"
    });
  } catch (err) {
    res.status(500).json({
      error: err.message
    });
  }
});


// Start server
app.listen(5000, () => {
  console.log("Server running at http://localhost:5000");
});