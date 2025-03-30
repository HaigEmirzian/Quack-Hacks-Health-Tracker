import { Link, useLocation } from "react-router-dom";

function Navbar() {
  const location = useLocation();

  // Set the page title based on the current path
  let pageTitle = "Health Data";
  if (location.pathname === "/weight") {
    pageTitle = "Weight Data";
  }

  // Base styles for links (excluding color)
  const baseLinkClass = "px-3 py-2 rounded-md text-sm font-medium no-underline";

  // Inline styles for Health Data link
  const healthDataStyle = {
    color: location.pathname === "/" ? "#FFFFFE" : "#949594", // black when active, gray-600 when inactive
    borderBottom: location.pathname === "/" ? "2px solid #FFFFFE" : "none",
    boxShadow: location.pathname === "/" ?'0px 5px 20px rgba(255, 255, 255, 0.4)' : "none", // Bottom shadow effect
  };

  // Inline styles for Weight Data link
  const weightDataStyle = {
    color: location.pathname === "/weight" ? "#FFFFFE" : "#949594", // black when active, gray-600 when inactive
    borderBottom: location.pathname === "/weight" ? "2px solid #FFFFFE" : "none",
    boxShadow: location.pathname === "/weight" ?'0px 5px 20px rgba(255, 255, 255, 0.4)' : "none", // Bottom shadow effect
  };

  return (
    <nav className="bg-white shadow"style={{ backgroundColor: "#9D1535", }}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex justify-between items-center h-16">
        {/* Dynamic Title */}
        <div className="flex items-center space-x-4">
          <img src="public/duck2.png" alt="icon" className="w-12 h-12" />
          <h1 className="text-base font-semibold text-white">{pageTitle}</h1>
        </div>
        {/* Navigation Links */}
        <div className="flex space-x-4">
          <Link
            to="/"
            className={baseLinkClass}
            style={healthDataStyle}
          >
            Health Data
          </Link>
          <Link
            to="/weight"
            className={baseLinkClass}
            style={weightDataStyle}
          >
            Weight Data
          </Link>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;