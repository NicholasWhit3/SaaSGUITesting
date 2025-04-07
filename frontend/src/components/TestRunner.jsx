import React, { useState } from "react";
import axios from "axios";

const API_URL = "http://127.0.0.1:8000/api";

const TestRunner = () => {
  const [figmaUrl, setFigmaUrl] = useState("");
  const [websiteUrl, setWebsiteUrl] = useState("");
  const [selectors, setSelectors] = useState("");
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");

  const runTest = async () => {
    if (!websiteUrl.trim()) {
      setError("Website URL is required!");
      return;
    }
    if (!figmaUrl.trim() && !selectors.trim()) {
      setError("Enter either Figma URL or CSS selectors!");
      return;
    }

    setError("");
    setStatus("Starting test...");
    setLoading(true);

    try {
      const response = await axios.post(`${API_URL}/run-test`, {
        figma_url: figmaUrl || null,
        website_url: websiteUrl,
        selectors: selectors || null,
      });

      setStatus("Processing results...");
      setResults({
        matched: response.data?.matched || [],
        differences: response.data?.differences || [],
      });
      setStatus("Test completed!");
    } catch (error) {
      console.error("Error running test", error);
      setError("An error occurred while running the test.");
      setStatus("Test failed.");
    }
    setLoading(false);
  };

  const downloadPDF = async () => {
    if (!results || (!results.matched.length && !results.differences.length)) {
      setError("No results available for PDF.");
      return;
    }

    try {
      await axios.post(`${API_URL}/store-differences`, { differences: results.differences });
      window.open(`${API_URL}/generate-pdf`, "_blank");
    } catch (error) {
      console.error("Error generating PDF", error);
      setError("Failed to generate PDF.");
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">GUI Testing Tool</h1>
      {error && <p className="text-red-500">{error}</p>}
      {status && <p className="text-blue-500">{status}</p>}

      <div className="mb-4">
        <input
          type="text"
          placeholder="Enter Website URL"
          value={websiteUrl}
          onChange={(e) => setWebsiteUrl(e.target.value)}
          className="border p-2 w-full mb-2"
        />
        <input
          type="text"
          placeholder="Enter Figma URL (optional)"
          value={figmaUrl}
          onChange={(e) => setFigmaUrl(e.target.value)}
          className="border p-2 w-full mb-2"
        />
        <input
          type="text"
          placeholder="Enter CSS Selectors (optional)"
          value={selectors}
          onChange={(e) => setSelectors(e.target.value)}
          className="border p-2 w-full"
        />
      </div>

      <button
        onClick={runTest}
        className={`px-4 py-2 rounded ${loading ? "bg-gray-400" : "bg-blue-500 text-white"}`}
        disabled={loading}
      >
        {loading ? "Testing..." : "Run Test"}
      </button>

      {results && (
        <div className="mt-4">
          <h2 className="text-xl font-bold">Comparison Results:</h2>

          {results.matched.length > 0 && (
            <>
              <h3 className="text-lg font-bold mt-2 text-green-600">✅ Matched Elements</h3>
              <ul className="border p-2">
                {results.matched.map((item, index) => (
                  <li key={index} className="border-b p-2 text-green-600">
                    <strong>{item}</strong>: All styles match! 🎉
                  </li>
                ))}
              </ul>
            </>
          )}

          {results.differences.length > 0 && (
            <>
              <h3 className="text-lg font-bold mt-2 text-red-500">❌ Differences</h3>
              <ul className="border p-2">
                {results.differences.map((diff, index) => (
                  <li key={index} className="border-b p-2 text-red-500">
                    <strong>{diff.element}</strong>: {diff.issue}
                    {diff.details && diff.details.length > 0 && (
                      <ul className="ml-4 text-sm text-gray-700">
                        {diff.details.map((d, i) => (
                          <li key={i}>- {d.property}: expected <b>{d.expected}</b>, got <b>{d.actual}</b></li>
                        ))}
                      </ul>
                    )}
                  </li>
                ))}
              </ul>
            </>
          )}

          <button
            onClick={downloadPDF}
            className="bg-green-500 text-white px-4 py-2 rounded mt-4"
          >
            Download PDF
          </button>
        </div>
      )}
    </div>
  );
};

export default TestRunner;
