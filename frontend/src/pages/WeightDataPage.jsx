import { useState, useEffect } from "react";
import FileUploadBox from "../components/FileUploadBox";

const backgrounds = [
  { image: "https://images.pexels.com/photos/40568/medical-appointment-doctor-healthcare-40568.jpeg" },
  { image: "https://images.pexels.com/photos/5214962/pexels-photo-5214962.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1" },
  { image: "https://t4.ftcdn.net/jpg/01/33/33/41/360_F_133334155_X23HzbJKawbIgXVaub4bPM8CjpkS5uMS.jpg" },
];

function WeightDataPage() {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [nextIndex, setNextIndex] = useState(1);
  const [isTransitioning, setIsTransitioning] = useState(false);
  document.title = "Quack Hacks - Health Summary";

  useEffect(() => {
    const interval = setInterval(() => {
      setIsTransitioning(true);

      setTimeout(() => {
        setCurrentIndex(nextIndex);
        setNextIndex((prev) => (prev + 1) % backgrounds.length);
        setIsTransitioning(false);
      }, 1000);
    }, 8000); // Change every 10 seconds

    return () => clearInterval(interval);
  }, [nextIndex]);

  return (
    <div className="relative min-h-screen w-screen flex items-center justify-center overflow-hidden">
      {/* Background Layers */}
      <div className="background-container">
        {/* Current Background (Moves Up) */}
        <div
          className={`background-layer ${isTransitioning ? "bg-transition-out" : ""}`}
          style={{ backgroundImage: `url(${backgrounds[currentIndex].image})` }}
        />

        {/* Next Background (Moves In) */}
        {isTransitioning && (
          <div
            className="background-layer bg-transition-in"
            style={{ backgroundImage: `url(${backgrounds[nextIndex].image})` }}
          />
        )}
      </div>

      {/* Content Box */}
      <div className="relative z-10 w-full max-w-3xl bg-white/80 backdrop-blur-lg rounded-2xl shadow-xl p-8 text-center mx-4">
        <h1 className="text-3xl sm:text-4xl font-semibold text-gray-800 mb-4">
          Track Your Weight Data
        </h1>
        <p className="text-gray-500 mb-6 text-base sm:text-lg">
          Measure your progress and predict your weight loss journey.
        </p>

        <FileUploadBox accept=".csv" onFileSelect={() => {}} labelText="Drag & drop CSV file here or click to choose" />

        <button className="mt-4 w-full bg-black text-white px-6 py-3 rounded-full hover:bg-gray-800 transition duration-200">
          Analyze Weight Data
        </button>
      </div>
    </div>
  );
}

export default WeightDataPage;
