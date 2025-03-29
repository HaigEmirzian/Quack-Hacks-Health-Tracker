import { useState } from "react";

function FileUploadBox({ accept, onFileSelect, labelText }) {
  const [fileName, setFileName] = useState("");

  const handleChange = (e) => {
    const selected = e.target.files[0];
    if (selected) {
      setFileName(selected.name);
      onFileSelect(selected);
    }
  };

  return (
    <label
      htmlFor="file-upload"
      className="block border-4 border-dashed border-gray-300 rounded-lg h-48 flex flex-col items-center justify-center cursor-pointer hover:border-black transition duration-200 bg-gray-50"
    >
      <span className="text-xl text-gray-700">
        {fileName || labelText || "Drag & drop file here or click to choose"}
      </span>
      <input
        id="file-upload"
        type="file"
        accept={accept}
        onChange={handleChange}
        className="hidden"
      />
    </label>
  );
}

export default FileUploadBox;
