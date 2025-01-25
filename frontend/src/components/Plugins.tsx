import React from "react";

interface PluginParams {
  [key: string]: any;
}

interface PluginComponentProps {
  params: PluginParams;
  handleChange: (key: string, value: any) => void;
}

export const pluginComponents: Record<string, React.FC<PluginComponentProps>> = {
  flip: ({ params, handleChange }) => (
    <div className="mb-3">
      <label htmlFor="flip-mode" className="block text-sm font-medium text-gray-600 mb-1">
        Mode
      </label>
      <select
        id="flip-mode"
        value={params.mode}
        onChange={(e) => handleChange("mode", e.target.value)}
        className="block w-full border border-gray-300 rounded-lg p-2 focus:outline-none focus:ring-2 focus:ring-blue-400"
      >
        <option value="vertical">Vertical</option>
        <option value="horizontal">Horizontal</option>
        <option value="both">Both</option>
      </select>
    </div>
  ),
  resize: ({ params, handleChange }) => (
    <>
      <div className="mb-3">
        <label htmlFor="resize-width" className="block text-sm font-medium text-gray-600 mb-1">
          Width (px)
        </label>
        <input
          id="resize-width"
          type="number"
          value={params.width}
          onChange={(e) => handleChange("width", e.target.value)}
          className="block w-full border border-gray-300 rounded-lg p-2 focus:outline-none focus:ring-2 focus:ring-blue-400"
        />
      </div>
      <div className="mb-3">
        <label htmlFor="resize-height" className="block text-sm font-medium text-gray-600 mb-1">
          Height (px)
        </label>
        <input
          id="resize-height"
          type="number"
          value={params.height}
          onChange={(e) => handleChange("height", e.target.value)}
          className="block w-full border border-gray-300 rounded-lg p-2 focus:outline-none focus:ring-2 focus:ring-blue-400"
        />
      </div>
    </>
  ),
  pad: ({ params, handleChange }) => (
    <>
      <div className="mb-3">
        <label htmlFor="pad-width" className="block text-sm font-medium text-gray-600 mb-1">
          Width (px)
        </label>
        <input
          id="pad-width"
          type="number"
          value={params.target_size[0]}
          onChange={(e) =>
            handleChange("target_size", [parseInt(e.target.value), params.target_size[1]])
          }
          className="block w-full border border-gray-300 rounded-lg p-2 focus:outline-none focus:ring-2 focus:ring-blue-400"
        />
      </div>
      <div className="mb-3">
        <label htmlFor="pad-height" className="block text-sm font-medium text-gray-600 mb-1">
          Height (px)
        </label>
        <input
          id="pad-height"
          type="number"
          value={params.target_size[1]}
          onChange={(e) =>
            handleChange("target_size", [params.target_size[0], parseInt(e.target.value)])
          }
          className="block w-full border border-gray-300 rounded-lg p-2 focus:outline-none focus:ring-2 focus:ring-blue-400"
        />
      </div>
      <div className="mb-3">
        <label htmlFor="pad-position" className="block text-sm font-medium text-gray-600 mb-1">
          Position
        </label>
        <select
          id="pad-position"
          value={params.position}
          onChange={(e) => handleChange("position", e.target.value)}
          className="block w-full border border-gray-300 rounded-lg p-2 focus:outline-none focus:ring-2 focus:ring-blue-400"
        >
          <option value="center">Center</option>
          <option value="top-left">Top Left</option>
          <option value="top-right">Top Right</option>
          <option value="bottom-left">Bottom Left</option>
          <option value="bottom-right">Bottom Right</option>
        </select>
      </div>
      <div className="mb-3">
        <label htmlFor="pad-color" className="block text-sm font-medium text-gray-600 mb-1">
          Background Color
        </label>
        <input
          id="pad-color"
          type="color"
          value={params.color || "#000000"}
          onChange={(e) => handleChange("color", e.target.value)}
          className="block w-16 h-10 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400"
        />
      </div>
    </>
  ),
};
