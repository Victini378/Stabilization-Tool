import tkinter as tk
from tkinter import messagebox, filedialog

from datetime import datetime
import platform
import cpuinfo

def generate_report(parameters, _output_path = None):
    
    stabilization_type = parameters['stabilization_type']
    max_shift_x = parameters['max_shift_x']
    max_shift_y = parameters['max_shift_y']
    roi_x = parameters['roi_x']
    roi_y = parameters['roi_y']
    roi_width = parameters['roi_width']
    roi_height = parameters['roi_height']
    max_level = parameters['max_level']
    eps = parameters['eps']
    count = parameters['count']
    factor = parameters['factor']

    # Get current date and time
    current_date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    # Get platform information
    os_info = platform.system() + " " + platform.release()
    cpu_info = cpuinfo.get_cpu_info()['brand_raw']

    # Convert stabilization type to title case for the HTML report
    stabilization_type_title = stabilization_type.title()

    # Create HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Stabilization Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1 {{ color: #2E3B4E; text-align: center; }}
            h2, h3 {{ color: #34495E; }}
            .section-header {{ background-color: #E9ECEF; padding: 10px; border-radius: 5px; }}
            .parameter-description {{ margin-top: 15px; }}
            .footer {{ margin-top: 30px; text-align: center; font-size: 0.8em; color: #777; }}
        </style>
    </head>
    <body>
        <h1>Stabilization Report</h1>

        <h2 class="section-header">General Information</h2>
        <p>This report has been generated to provide a comprehensive analysis of the parameters used in the video stabilization process. Each parameter is described with its function and the value used.</p>
        <p><strong>Report Creation Date:</strong> {current_date}</p>
        <p><strong>Platform:</strong> {os_info}</p>
        <p><strong>CPU:</strong> {cpu_info}</p>

        <h2 class="section-header">Stabilization Type</h2>
        <div class="parameter-description">
            <h3>{stabilization_type_title} Stabilization</h3>
            {"<div><p><strong>Description:</strong> Local stabilization focuses on correcting small, localized regions within the video frame. This approach is particularly useful when dealing with minor camera shakes or slight movements. It involves identifying and stabilizing specific areas of the frame independently, which can be effective for reducing small jitters while preserving the overall content and perspective of the video. The algorithm analyzes local features and applies corrections that minimize visible disruptions in the localized regions.</p></div>" if stabilization_type == "local" else ""}
            {"<div><p><strong>Description:</strong> Global stabilization aims to correct movements across the entire video frame. This method is suitable for scenarios where there are larger shifts or more extensive stabilization needs. It typically involves estimating the global motion across the entire frame and applying corrections to compensate for significant camera movements or shakes. This approach can be effective in stabilizing footage where the camera might have moved significantly, ensuring that the overall video frame remains steady.</p></div>" if stabilization_type == "global" else ""}
            {"<div><p><strong>Description:</strong> Perspective stabilization is designed to handle changes in the camera's viewpoint, such as when the camera pans or tilts. This method accounts for alterations in the perspective of the video, making it suitable for scenarios where the camera movement changes the scene's viewpoint. It involves correcting distortions and ensuring that the video appears stable despite significant changes in the perspective. This type of stabilization is useful for maintaining a consistent viewpoint and preventing distortions in footage where the camera has moved in a non-linear fashion.</p></div>" if stabilization_type == "perspective" else ""}
        </div>

        <h2 class="section-header">Parameters</h2>
        {"<div class='parameter-description'><h3>Max Shift X</h3><p><strong>Description:</strong> This parameter determines the maximum horizontal shift (in pixels) allowed during stabilization. A higher value allows a wider correction of horizontal movements, which is useful for handling larger horizontal shifts in global stabilization scenarios.</p><p><strong>Value:</strong> " + str(max_shift_x) + " pixels</p></div>" if stabilization_type == "global" and max_shift_x is not None else ""}
        {"<div class='parameter-description'><h3>Max Shift Y</h3><p><strong>Description:</strong> This parameter defines the maximum vertical shift (in pixels). It helps to limit the correction of vertical movements during stabilization. Increasing this value accommodates larger vertical shifts, especially useful in global stabilization.</p><p><strong>Value:</strong> " + str(max_shift_y) + " pixels</p></div>" if stabilization_type == "global" and max_shift_y is not None else ""}

        {"<div class='parameter-description'><h3>ROI X and Y</h3><p><strong>Description:</strong> The X and Y coordinates of the top-left corner of the Region of Interest (ROI). This defines the specific area of the video that is focused on for stabilization analysis. In local and perspective stabilization, selecting the appropriate ROI helps in targeting the most relevant parts of the frame for accurate stabilization.</p><p><strong>X Value:</strong> " + str(roi_x) + "</p><p><strong>Y Value:</strong> " + str(roi_y) + "</p></div>" if stabilization_type in ["local", "perspective"] and roi_x is not None and roi_y is not None else ""}
        {"<div class='parameter-description'><h3>ROI Width and Height</h3><p><strong>Description:</strong> Width and height of the ROI. These parameters define the size of the area of the video that is analyzed for stabilization. Properly setting the ROI dimensions ensures that the relevant portions of the video are effectively stabilized, which is crucial for local and perspective stabilization.</p><p><strong>Width:</strong> " + str(roi_width) + " pixels</p><p><strong>Height:</strong> " + str(roi_height) + " pixels</p></div>" if stabilization_type in ["local", "perspective"] and roi_width is not None and roi_height is not None else ""}

        {"<div class='parameter-description'><h3>Max Level</h3><p><strong>Description:</strong> The maximum pyramid level used for processing. Higher levels provide more precision in stabilization but require more computing resources. This parameter affects the detail level at which stabilization is applied, with higher levels offering finer corrections at the cost of increased computational demand.</p><p><strong>Value:</strong> " + str(max_level) + "</p></div>" if max_level is not None else ""}
        {"<div class='parameter-description'><h3>Eps</h3><p><strong>Description:</strong> The error threshold (epsilon) used for the stabilization algorithm convergence. Lower values improve precision but may increase computation time. This parameter controls the convergence criteria of the stabilization algorithm, influencing the accuracy and speed of the stabilization process.</p><p><strong>Value:</strong> " + str(eps) + "</p></div>" if eps is not None else ""}
        {"<div class='parameter-description'><h3>Count</h3><p><strong>Description:</strong> The number of iterations or the maximum number of samples considered during the analysis. A higher count can improve the quality of the final stabilization result by allowing more thorough analysis, but it also increases the processing time.</p><p><strong>Value:</strong> " + str(count) + "</p></div>" if count is not None else ""}
        {"<div class='parameter-description'><h3>Factor</h3><p><strong>Description:</strong> The `factor` parameter controls the density of points of interest used for the calculation of motion within the region of interest (ROI). A higher value indicates a larger number of points, which can improve the accuracy of motion estimation, but also increases the computational load. The optimal value of `factor` depends on the complexity of the video and the available computational resources.</p><p><strong>Value:</strong> " + str(factor) + "</p></div>" if factor is not None else ""}


        <div class="footer">
            <p>This software is distributed as free software under the GPLv3 License, which allows modification and redistribution of the source code.</p>
        </div>
    </body>
    </html>
    """

    if _output_path is None:
        output_path = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML files", "*.html"), ("All files", "*.*")]
        )
    else:
        output_path = _output_path

    if output_path:
        with open(output_path, "w") as file:
            file.write(html_content)

        if _output_path is None:
            messagebox.showinfo("Success", "Report generated successfully!")
        else:
            print("Report generated successfully!")