import cv2

import os
import argparse

from stabilizing import local_stabilizer_video, global_stabilizer_video, perspective_stabilizer_video
from report import generate_report

def select_roi(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error loading video")
        return None

    ret, first_frame = cap.read()
    if not ret:
        print("Error loading first frame")
        cap.release()
        return None

    x, y, w, h = cv2.selectROI("Select a ROI and ENTER", first_frame, fromCenter=False, showCrosshair=True)
    cv2.destroyWindow("Select a ROI and ENTER")
    cap.release()
    return x, y, w, h

def get_parameters(args):
    default_params = {
        'max_level': 10,
        'eps': 0.01,
        'count': 30,
        'factor': 4
    }

    max_shift_x = max_shift_y = None
    if args.stabilization_type == 'global':
        max_shift_x = args.max_shift_x
        max_shift_y = args.max_shift_y

    max_level = args.max_level if args.max_level is not None else default_params['max_level']
    eps = args.eps if args.eps is not None else default_params['eps']
    count = args.count if args.count is not None else default_params['count']
    factor = args.factor if args.factor is not None else default_params['factor']

    return max_shift_x, max_shift_y, max_level, eps, count, factor

def process_stabilization_choice(args):
    roi = None
    if args.roi_x is not None and args.roi_y is not None and args.roi_width is not None and args.roi_height is not None:
        roi = (args.roi_x, args.roi_y, args.roi_width, args.roi_height)
    elif args.stabilization_type in ['local', 'perspective']:
        roi = select_roi(args.video_path)
        if roi is None:
            print("ROI selection failed.")
            return
    x, y, w, h = roi if roi else (0, 0, 0, 0)

    max_shift_x, max_shift_y, max_level, eps, count, factor = get_parameters(args)

    return {
        'stabilization_type': args.stabilization_type,
        'max_shift_x': max_shift_x,
        'max_shift_y': max_shift_y,
        'roi_x': x,
        'roi_y': y,
        'roi_width': w,
        'roi_height': h,
        'max_level': max_level,
        'eps': eps,
        'count': count,
        'factor': factor
    }

def run_stabilization(video_path, output_path, args):
    if args['stabilization_type'] == 'local':
        print("Starting local stabilization...")
        local_stabilizer_video(video_path, output_path, [args['max_level'], args['eps'], args['count']], [args['roi_x'], args['roi_y'], args['roi_width'], args['roi_height']], args['factor'])
    elif args['stabilization_type'] == 'global':
        if max_shift_x is None or max_shift_y is None:
            print("Max shift values are required for global stabilization.")
            return
        print("Starting global stabilization...")
        global_stabilizer_video(video_path, output_path, [args['max_level'], args['eps'], args['count']], args['max_shift_x'], args['max_shift_y'], args['factor'])
    elif args['stabilization_type'] == 'perspective':
        print("Starting perspective stabilization...")
        perspective_stabilizer_video(video_path, output_path, [args['max_level'], args['eps'], args['count']], [args['roi_x'], args['roi_y'], args['roi_width'], args['roi_height']], args['factor'])
    else:
        print("Invalid stabilization type. Exiting.")
        return

    print("Stabilization completed.")

def main():
    parser = argparse.ArgumentParser(description="Video Stabilization script by Giuseppe Tomarchio")
    parser.add_argument("-i", "--input", dest="video_path", required=True, help="Path to the input video file")
    parser.add_argument("output_path", help="Path for the output video")
    parser.add_argument("-t", "--stabilization_type", choices=['local', 'global', 'perspective'], required=True, help="Type of stabilization")
    parser.add_argument("-msx", "--max_shift_x", type=int, help="Max shift X for global stabilization")
    parser.add_argument("-msy", "--max_shift_y", type=int, help="Max shift Y for global stabilization")
    parser.add_argument("-ml", "--max_level", type=int, help="Max level for stabilization")
    parser.add_argument("-e", "--eps", type=float, help="EPS value for stabilization")
    parser.add_argument("-c", "--count", type=int, help="Count value for stabilization")
    parser.add_argument("-f", "--factor", type=int, help="Factor for stabilization")
    parser.add_argument("-rx", "--roi_x", type=int, help="ROI X coordinate")
    parser.add_argument("-ry", "--roi_y", type=int, help="ROI Y coordinate")
    parser.add_argument("-rw", "--roi_width", type=int, help="ROI Width")
    parser.add_argument("-rh", "--roi_height", type=int, help="ROI Height")
    parser.add_argument("-r", "--report", help="Generate a report after stabilization")

    args = parser.parse_args()

    if not os.path.isfile(args.video_path):
        print("Invalid video path")
        return

    if not args.output_path:
        print("Invalid output path")
        return

    parameters = process_stabilization_choice(args)

    run_stabilization(args.video_path, args.output_path, parameters)

    if args.report is not None:
        generate_report(parameters, args.report)

if __name__ == "__main__":
    main()