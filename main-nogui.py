import cv2
import os
import argparse
from stabilizing import local_stabilizer_video, global_stabilizer_video, perspective_stabilizer_video

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

def get_default_parameters():
    return {
        'max_level': 10,
        'eps': 0.01,
        'count': 30,
        'factor': 4
    }

def get_parameters(stabilization_type, args):
    default_params = get_default_parameters()

    max_shift_x = max_shift_y = None
    if stabilization_type == 'global':
        max_shift_x = args.max_shift_x
        max_shift_y = args.max_shift_y

    max_level = args.max_level if args.max_level is not None else default_params['max_level']
    eps = args.eps if args.eps is not None else default_params['eps']
    count = args.count if args.count is not None else default_params['count']
    factor = args.factor if args.factor is not None else default_params['factor']

    return max_shift_x, max_shift_y, max_level, eps, count, factor

def process_stabilization_choice(choice, video_path, output_path, args):
    roi = None
    if args.roi_x is not None and args.roi_y is not None and args.roi_width is not None and args.roi_height is not None:
        roi = (args.roi_x, args.roi_y, args.roi_width, args.roi_height)
    elif choice in ['1', '3']:
        roi = select_roi(video_path)
        if roi is None:
            print("ROI selection failed.")
            return
    x, y, w, h = roi if roi else (0, 0, 0, 0)

    max_shift_x, max_shift_y, max_level, eps, count, factor = get_parameters(choice, args)

    if choice == '1':
        print("Starting local stabilization...")
        local_stabilizer_video(video_path, output_path, [max_level, eps, count], [x, y, w, h], factor)
    elif choice == '2':
        if max_shift_x is None or max_shift_y is None:
            print("Max shift values are required for global stabilization.")
            return
        print("Starting global stabilization...")
        global_stabilizer_video(video_path, output_path, [max_level, eps, count], max_shift_x, max_shift_y, factor)
    elif choice == '3':
        print("Starting perspective stabilization...")
        perspective_stabilizer_video(video_path, output_path, [max_level, eps, count], [x, y, w, h], factor)
    else:
        print("Invalid choice. Exiting.")
        return

    print("Stabilization completed.")

def main():
    parser = argparse.ArgumentParser(description="Video Stabilization")
    parser.add_argument("video_path", help="Path to the video file")
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

    args = parser.parse_args()

    if not os.path.isfile(args.video_path):
        print("Invalid video path")
        return

    if not args.output_path:
        print("Invalid output path")
        return

    choice_map = {'local': '1', 'global': '2', 'perspective': '3'}
    choice = choice_map[args.stabilization_type]

    process_stabilization_choice(choice, args.video_path, args.output_path, args)

if __name__ == "__main__":
    main()