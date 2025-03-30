import { useState } from "react";
import FileUploadBox from "../components/FileUploadBox";
import RingLoader from "react-spinners/RingLoader";

function HealthDataPage() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [overallInsight, setOverallInsight] = useState(null);
  const [loading, setLoading] = useState(false);
  const [overallLoading, setOverallLoading] = useState(false);

  const handleFileSelect = (selectedFile) => {
    setFile(selectedFile);
  };

  // Mapping for metric headings
  const headingMap = {
    "activeenergyburned.csv": "Active Energy Burned",
    "heartrate.csv": "Heart Rate",
    "stepcount.csv": "Step Count",
  };

  // Fetch overall insights from the backend endpoint
  const fetchOverallInsight = async () => {
    setOverallLoading(true);
    try {
      const res = await fetch("http://localhost:5000/overallInsights");
      if (!res.ok) {
        const errorData = await res.json();
        setOverallInsight({ error: errorData.error || "An unknown error occurred." });
      } else {
        // In this example, the endpoint returns plain text; adjust if it returns JSON
        const data = await res.text();
        setOverallInsight(data);
      }
    } catch (err) {
      console.error("Overall insights fetch failed", err);
      setOverallInsight({ error: "Failed to fetch overall insights." });
    } finally {
      setOverallLoading(false);
    }
  };

  // Handle file upload and subsequent overall insights fetching
  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    setResult(null);
    setOverallInsight(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("http://localhost:5000/appleDataUpload", {
        method: "POST",
        body: formData,
      });
      if (!res.ok) {
        const errorData = await res.json();
        setResult({ error: errorData.error || "An unknown error occurred." });
      } else {
        const data = await res.json();
        setResult(data);
        // After a successful upload, fetch the overall insights
        await fetchOverallInsight();
      }
    } catch (err) {
      console.error("Upload failed", err);
      setResult({ error: "Failed to fetch insights." });
    } finally {
      setLoading(false);
    }
  };

  // Map file names to image URLs (adjust these paths as needed)
  const imageMapping = {
    "activeenergyburned.csv": "/assets/activeenergyburned.png",
    "heartrate.csv": "/assets/heartrate.png",
    "stepcount.csv": "/assets/stepcount.png",
  };

  // Determine if insights are available
  const hasMetricInsights =
    result && result.insights && Object.keys(result.insights).length > 0;
  const showInsightsContainer = hasMetricInsights || overallInsight;

  return (
    <div className="min-h-screen w-screen bg-gradient-to-b from-white to-gray-100 flex items-center justify-center p-4">
      <div className="relative w-full max-w-3xl bg-white rounded-2xl shadow-xl p-8 text-center mx-4">
        <h1 className="text-3xl sm:text-4xl font-semibold text-gray-800 mb-4">
          Import Your Apple Health Data
        </h1>
        <p className="text-gray-500 mb-6 text-base sm:text-lg">
          Unlock valuable insights into your well-being.
        </p>

        <FileUploadBox
          accept=".xml"
          onFileSelect={handleFileSelect}
          labelText="Drag & drop file here or click to choose"
        />

        <button
          onClick={handleUpload}

          className="mt-4 w-full bg-black text-white px-6 py-3 rounded-full hover:bg-gray-800 transition duration-200"
          disabled={loading || overallLoading}

        >
          {loading ? "Analyzing..." : "Get Insights"}
        </button>

        {showInsightsContainer && (
          <div className="mt-6 text-left">
            {result && result.error ? (
              <div className="text-red-500 text-lg">{result.error}</div>
            ) : (
              <>
                <div className="flex flex-col space-y-4">
                  {hasMetricInsights &&
                    Object.entries(result.insights).map(([key, text]) => (
                      <div
                        key={key}
                        className="flex items-center bg-gray-100 p-4 rounded-lg shadow"
                      >
                        <img
                          src={imageMapping[key] || "/assets/default.png"}
                          alt={key}
                          className="w-24 h-24 object-contain mr-4"
                        />
                        <div>
                          <h3 className="font-semibold text-gray-800 mb-1">
                            {headingMap[key] || key.replace(".csv", "")}
                          </h3>
                          <p className="text-gray-600 text-sm">{text}</p>
                        </div>
                      </div>
                    ))}
                  {overallInsight && (
                    <div className="flex items-center bg-gray-100 p-4 rounded-lg shadow">
                      <img
                        src="/assets/overall.png"
                        alt="Overall Health"
                        className="w-24 h-24 object-contain mr-4"
                      />
                      <div>
                        <h3 className="font-semibold text-gray-800 mb-1">
                          Overall Health
                        </h3>
                        <p className="text-gray-600 text-sm">
                          {overallInsight.error
                            ? overallInsight.error
                            : overallInsight}
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              </>
            )}
          </div>
        )}

        {(loading || overallLoading) && (
          <div className="absolute inset-0 flex items-center justify-center bg-white bg-opacity-80 rounded-2xl">
            <RingLoader color="#007AFF" size={90} speedMultiplier={1.2} />
          </div>
        )}
      </div>
    </div>
  );
}

export default HealthDataPage;