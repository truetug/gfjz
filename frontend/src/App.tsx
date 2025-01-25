import React, { useState } from "react";
import "./index.css"; // Import Tailwind CSS
import { DndProvider, useDrag, useDrop } from "react-dnd";
import { HTML5Backend } from "react-dnd-html5-backend";
import { pluginComponents } from "./components/Plugins";

interface Plugin {
  id: number;
  plugin: string;
  params: { [key: string]: any };
}

function DraggablePlugin({
  plugin,
  index,
  movePlugin,
  handlePluginChange,
  removePlugin,
}: {
  plugin: Plugin;
  index: number;
  movePlugin: (dragIndex: number, hoverIndex: number) => void;
  handlePluginChange: (index: number, key: string, value: any) => void;
  removePlugin: (index: number) => void;
}) {
  const ref = React.useRef<HTMLDivElement>(null);
  const [, drop] = useDrop({
    accept: "PLUGIN",
    hover(item: { index: number }, monitor) {
      if (!ref.current) return;
      const dragIndex = item.index;
      const hoverIndex = index;

      if (dragIndex === hoverIndex) return;

      const hoverBoundingRect = ref.current?.getBoundingClientRect();
      const hoverMiddleY =
        (hoverBoundingRect.bottom - hoverBoundingRect.top) / 2;
      const clientOffset = monitor.getClientOffset();
      const hoverClientY = clientOffset!.y - hoverBoundingRect.top;

      if (dragIndex < hoverIndex && hoverClientY < hoverMiddleY) return;
      if (dragIndex > hoverIndex && hoverClientY > hoverMiddleY) return;

      movePlugin(dragIndex, hoverIndex);
      item.index = hoverIndex;
    },
  });

  const [{ isDragging }, drag] = useDrag({
    type: "PLUGIN",
    item: { index },
    collect: (monitor) => ({
      isDragging: monitor.isDragging(),
    }),
  });

  drag(drop(ref));

  const PluginComponent = pluginComponents[plugin.plugin];

  return (
    <div
      ref={ref}
      className={`rounded-lg p-4 mb-4 flex items-start bg-gray-50 shadow-sm ${
        isDragging ? "opacity-50" : ""
      }`}
    >
      <div
        className="w-6 h-full bg-gray-300 rounded-l cursor-grab hover:bg-gray-400"
        title="Drag to reorder"
      />
      <div className="flex-1 ml-4">
        <div className="mb-3 flex justify-between items-center">
          <span className="font-semibold text-gray-800 text-lg">{plugin.plugin}</span>
          <button
            onClick={() => removePlugin(index)}
            className="text-red-500 hover:text-red-700"
          >
            Remove
          </button>
        </div>
        {PluginComponent && (
          <PluginComponent
            params={plugin.params}
            handleChange={(key, value) => handlePluginChange(index, key, value)}
          />
        )}
      </div>
    </div>
  );
}

function App() {
  const [file, setFile] = useState<File | null>(null);
  const [fileDetails, setFileDetails] = useState<{
    format: string;
    frameCount: number;
    fileSize: string;
    dimensions: string;
  } | null>(null);
  const [plugins, setPlugins] = useState<Plugin[]>([
    { id: 1, plugin: "resize", params: { size: [200, 200] } },
    { id: 2, plugin: "flip", params: { mode: "vertical" } },
    { id: 3, plugin: "pad", params: { target_size: [400, 400], position: "center", color: "#ffffff" } },
  ]);
  const [outputFormat, setOutputFormat] = useState("GIF");
  const [createPreview, setCreatePreview] = useState(true);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [archiveUrl, setArchiveUrl] = useState<string | null>(null);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selectedFile = e.target.files[0];
      setFile(selectedFile);

      // Extract file details
      const fileReader = new FileReader();
      fileReader.onload = (event) => {
        const arrayBuffer = event.target?.result;
        if (arrayBuffer) {
          const blob = new Blob([arrayBuffer]);
          const objectUrl = URL.createObjectURL(blob);

          const img = new Image();
          img.onload = () => {
            const format = selectedFile.type;
            const frameCount = 1; // Assuming 1 frame unless processing animated GIFs
            const fileSize = (selectedFile.size / 1024).toFixed(2) + " KB";
            const dimensions = `${img.width}x${img.height}`;

            setFileDetails({ format, frameCount, fileSize, dimensions });
            URL.revokeObjectURL(objectUrl);
          };
          img.src = objectUrl;
        }
      };
      fileReader.readAsArrayBuffer(selectedFile);
    }
  };

  const handlePluginChange = (index: number, key: string, value: any) => {
    const newPlugins = [...plugins];
    newPlugins[index].params[key] = value;
    setPlugins(newPlugins);
  };

  const movePlugin = (dragIndex: number, hoverIndex: number) => {
    const newPlugins = [...plugins];
    const [draggedPlugin] = newPlugins.splice(dragIndex, 1);
    newPlugins.splice(hoverIndex, 0, draggedPlugin);
    setPlugins(newPlugins);
  };

  const removePlugin = (index: number) => {
    const newPlugins = plugins.filter((_, i) => i !== index);
    setPlugins(newPlugins);
  };

  const addPlugin = (pluginType: string) => {
    const newPlugin: Plugin = {
      id: Date.now(),
      plugin: pluginType,
      params: pluginType === "resize"
        ? { size: [100, 100] }
        : pluginType === "flip"
        ? { mode: "vertical" }
        : { target_size: [200, 200], position: "center", color: "#ffffff" },
    };
    setPlugins([...plugins, newPlugin]);
  };

  const handleSubmit = async () => {
    if (!file) {
      alert("Please upload a file");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append(
      "config",
      JSON.stringify({
        pipeline: plugins,
        create_preview: createPreview,
        output_format: outputFormat,
      })
    );

    try {
      const response = await fetch("http://localhost:8000/process", {
        method: "POST",
        body: formData,
      });

      if (response.headers.get("Content-Type")?.includes("image/gif")) {
        const blob = await response.blob();
        setPreviewUrl(URL.createObjectURL(blob));
      } else {
        const blob = await response.blob();
        setArchiveUrl(URL.createObjectURL(blob));
      }
    } catch (error) {
      console.error("Error submitting request:", error);
    }
  };

  return (
    <DndProvider backend={HTML5Backend}>
      <header className="bg-blue-600 text-white py-4 text-center font-bold text-xl">
        GIF Processor Service
      </header>
      <div className="p-6 max-w-full mx-auto bg-white rounded-lg shadow-md grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h2 className="text-2xl font-bold text-center mb-6 text-gray-900">
            Plugins
          </h2>
          {plugins.map((plugin, index) => (
            <DraggablePlugin
              key={plugin.id}
              plugin={plugin}
              index={index}
              movePlugin={movePlugin}
              handlePluginChange={handlePluginChange}
              removePlugin={removePlugin}
            />
          ))}
          <div className="mt-4">
            <label htmlFor="add-plugin" className="block text-lg font-medium text-gray-800 mb-2">
              Add Plugin
            </label>
            <select
              id="add-plugin"
              onChange={(e) => addPlugin(e.target.value)}
              defaultValue=""
              className="block w-full border border-gray-300 rounded-lg p-2 focus:outline-none focus:ring-2 focus:ring-blue-400"
            >
              <option value="" disabled>
                Select plugin to add
              </option>
              <option value="resize">Resize</option>
              <option value="flip">Flip</option>
              <option value="pad">Pad</option>
            </select>
          </div>
        </div>

        <div className="border border-gray-300 rounded-lg p-4 bg-gray-50 shadow-sm">
          <h2 className="text-2xl font-bold text-center mb-6 text-gray-900">
            Settings
          </h2>
          <div className="mb-6">
            <label htmlFor="upload-file" className="block text-lg font-medium text-gray-800 mb-2">
              Upload File
            </label>
            <input
              id="upload-file"
              type="file"
              accept="image/gif"
              onChange={handleFileChange}
              className="block w-full border border-gray-300 rounded-lg p-3 bg-white shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
            />
          </div>

          {fileDetails && (
            <div className="mb-6">
              <h3 className="text-xl font-semibold text-gray-900 mb-3">File Details</h3>
              <ul className="list-disc pl-5 text-gray-800">
                <li>Format: {fileDetails.format}</li>
                <li>Frames: {fileDetails.frameCount}</li>
                <li>File Size: {fileDetails.fileSize}</li>
                <li>Dimensions: {fileDetails.dimensions}</li>
              </ul>
            </div>
          )}

          <div className="mb-6">
            <label htmlFor="output-format" className="block text-lg font-medium text-gray-800 mb-2">
              Output Format
            </label>
            <select
              id="output-format"
              value={outputFormat}
              onChange={(e) => setOutputFormat(e.target.value)}
              className="block w-full border border-gray-300 rounded-lg p-3 bg-white shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
            >
              <option value="GIF">GIF</option>
              <option value="PNG">PNG</option>
              <option value="JPEG">JPEG</option>
            </select>
          </div>

          <div className="mb-6 flex items-center">
            <input
              id="generate-preview"
              type="checkbox"
              checked={createPreview}
              onChange={(e) => setCreatePreview(e.target.checked)}
              className="mr-2"
            />
            <label htmlFor="generate-preview" className="text-lg font-medium text-gray-800">
              Generate Preview
            </label>
          </div>

          {previewUrl && (
            <div className="mb-6">
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Preview</h3>
              <img
                src={previewUrl}
                alt="Preview"
                className="border border-gray-300 rounded-lg shadow-lg"
              />
            </div>
          )}

          {archiveUrl && (
            <div className="mb-6">
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Download Frames</h3>
              <a
                href={archiveUrl}
                download="frames.zip"
                className="bg-blue-500 text-white px-6 py-3 rounded-lg shadow-lg text-lg font-semibold hover:bg-blue-600"
              >
                Download ZIP
              </a>
            </div>
          )}
        </div>

        <div className="mb-6 flex justify-center md:col-span-2">
          <button
            onClick={handleSubmit}
            className="bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg text-lg font-semibold hover:bg-green-600"
          >
            Generate
          </button>
        </div>
      </div>
      <footer className="bg-gray-800 text-white py-4 text-center font-medium">
        © 2025 GIF Processor. All rights reserved.
      </footer>
    </DndProvider>
  );
}

export default App;
