import cv2
import numpy as np

def draw_progress_bar(image, progress, bar_height=15):
    bar_width = image.shape[1]
    bar_x = 0
    bar_y = image.shape[0]

    img_with_bar = np.zeros((image.shape[0] + bar_height, bar_width, 3), dtype=np.uint8)
    img_with_bar[:image.shape[0], :] = image

    cv2.rectangle(img_with_bar, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (200, 200, 200), -1)
    
    completed_width = int(bar_width * progress)
    cv2.rectangle(img_with_bar, (bar_x, bar_y), (bar_x + completed_width, bar_y + bar_height), (6, 176, 37), -1)
    
    return img_with_bar

def initialize_points(_points, _factor = 4):
    points = []
    x,y,w,h = _points
    step_x, step_y = w // _factor, h // _factor
    for i in range(1, _factor):
        for j in range(1, _factor):
            points.append((x + i * step_x, y + j * step_y))
    return np.array(points, dtype=np.float32).reshape(-1, 1, 2)

def local_stabilizer_video(video_path, output_path, lkparams, roi, factor = 4):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error loading video")
        return

    ret, first_frame = cap.read()
    if not ret:
        print("Error loading first frame")
        cap.release()
        return

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    frame_buffer = [first_frame.copy()]

    x, y, w, h = roi
    center_x = x + w // 2
    center_y = y + h // 2

    points_to_track = initialize_points(roi, factor)

    lk_params = dict(winSize=(int(h*2), int(h*2)), maxLevel=lkparams[0], criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, lkparams[2], lkparams[1]))
    prev_gray = cv2.cvtColor(first_frame, cv2.COLOR_BGR2GRAY)

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_path, fourcc, int(cap.get(cv2.CAP_PROP_FPS)), (first_frame.shape[1], first_frame.shape[0]))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_buffer.append(frame)

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        new_points, status, _ = cv2.calcOpticalFlowPyrLK(prev_gray, gray, points_to_track, None, **lk_params)

        if status.sum() >= 4:
            valid_points = new_points[status == 1]
            new_center_x = np.mean(valid_points[:, 0])
            new_center_y = np.mean(valid_points[:, 1])

            dx = center_x - new_center_x
            dy = center_y - new_center_y

            T = np.float32([[1, 0, dx], [0, 1, dy]])
            for frame_x in frame_buffer:
                s_frame = frame_x.copy()
                for point in new_points:
                    x, y = point.ravel()
                    cv2.circle(frame_x, (int(x), int(y)), 3, (int(x), int(y), 0), -1)

                stabilized_frame = cv2.warpAffine(s_frame, T, (frame.shape[1], frame.shape[0]))

                out.write(stabilized_frame)
                concatenated_frame = np.hstack((frame_x, stabilized_frame))
                current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES)) - 1
                cv2.imshow("Converting...", draw_progress_bar(concatenated_frame, current_frame/frame_count))

            frame_buffer = []

            prev_gray = gray.copy()
            points_to_track = new_points
        else:
            print("Error in point tracking")
            prev_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if cv2.waitKey(30) & 0xFF == ord('q'):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print("Local stabilization completed and video saved in:", output_path)


def global_stabilizer_video(video_path, output_path, lkparams, max_shift_x, max_shift_y, factor = 4):
    global rect
    rect = (0, 0, 0, 0)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error loading video")
        return

    ret, first_frame = cap.read()
    if not ret:
        print("Error loading first frame")
        cap.release()
        return

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    x, y = (0,0)
    center_x = x + w // 2
    center_y = y + h // 2

    points_to_track = initialize_points((x,y,w,h), factor)

    lk_params = dict(winSize=(int(h*2), int(h*2)), maxLevel=lkparams[0], criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, lkparams[2], lkparams[1]))
    prev_gray = cv2.cvtColor(first_frame, cv2.COLOR_BGR2GRAY)

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_path, fourcc, int(cap.get(cv2.CAP_PROP_FPS)), (first_frame.shape[1], first_frame.shape[0]))

    frame_buffer = [first_frame.copy()]

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_buffer.append(frame)

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        new_points, status, _ = cv2.calcOpticalFlowPyrLK(prev_gray, gray, points_to_track, None, **lk_params)

        if status.sum() >= 4:
            valid_points = new_points[status == 1]
            new_center_x = np.mean(valid_points[:, 0])
            new_center_y = np.mean(valid_points[:, 1])

            dx = center_x - new_center_x
            dy = center_y - new_center_y

            T = np.float32([[1, 0, dx+max_shift_x], [0, 1, dy+max_shift_y]])
            for frame_x in frame_buffer:
                s_frame = frame_x.copy()
                for point in new_points:
                    x, y = point.ravel()
                    cv2.circle(frame_x, (int(x), int(y)), 3, (int(x), int(y), 0), -1)

                stabilized_frame = cv2.warpAffine(s_frame, T, (frame.shape[1], frame.shape[0]))

                out.write(stabilized_frame)
                concatenated_frame = np.hstack((frame_x, stabilized_frame))
                current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES)) - 1
                cv2.imshow("Converting...", draw_progress_bar(concatenated_frame, current_frame/frame_count))

            frame_buffer = []

            prev_gray = gray.copy()
            points_to_track = new_points
        else:
            print("Error in point tracking")
            prev_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if cv2.waitKey(30) & 0xFF == ord('q'):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print("Global stabilization completed and video saved in:", output_path)


def moving_average_filter(transformations, window_size=5):
    averaged_transformations = []
    for i in range(len(transformations)):
        if i < window_size:
            avg = np.mean(transformations[:i+1], axis=0)
        else:
            avg = np.mean(transformations[i-window_size+1:i+1], axis=0)
        averaged_transformations.append(avg)
    return averaged_transformations

def exponential_moving_average(H_list, alpha=0.2):
    smoothed_H = np.eye(3)
    for H in H_list:
        smoothed_H = (1 - alpha) * smoothed_H + alpha * H
        smoothed_H /= smoothed_H[2, 2]
    return smoothed_H

def perspective_stabilizer_video(video_path, output_path, lkparams, roi, factor = 4):
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Error opening video")
        return

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_rate = int(cap.get(cv2.CAP_PROP_FPS))
    
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_path, fourcc, frame_rate, (frame_width, frame_height))
    
    ret, prev_frame = cap.read()
    if not ret:
        print("Error when reading the first frame")
        return

    frame_buffer = [prev_frame.copy()]
    
    x, y, w, h = roi
    prev_pts = initialize_points((x,y,w,h), factor)
    
    lk_params = dict(winSize=(int(h*2), int(h*2)), maxLevel=lkparams[0], criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, lkparams[2], lkparams[1]))
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    
    H_matrices = []
    smoothed_H = np.eye(3)
    H = np.eye(3)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_buffer.append(frame.copy())
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        if prev_pts is not None:
            curr_pts, status, err = cv2.calcOpticalFlowPyrLK(prev_gray, gray, prev_pts, None, **lk_params)
        
            valid_prev_pts = prev_pts[status == 1]
            valid_curr_pts = curr_pts[status == 1]
            
            if len(valid_prev_pts) >= 4 and len(valid_curr_pts) >= 4:
                H_new, _ = cv2.findHomography(valid_prev_pts, valid_curr_pts, cv2.RANSAC)
                
                if H_new is not None:
                    H_matrices.append(H_new)
                    smoothed_H = exponential_moving_average(H_matrices, alpha=0.2)
                    H = smoothed_H.dot(H)
        
        for frame_x in frame_buffer:
            s_frame = frame_x.copy()
            for point in curr_pts:
                c_x, c_y = point.ravel()
                cv2.circle(frame_x, (int(c_x), int(c_y)), 3, (int(c_x), int(c_y), 0), -1)

            stabilized_frame = cv2.warpPerspective(s_frame, H, (s_frame.shape[1], s_frame.shape[0]))

            out.write(stabilized_frame)
            concatenated_frame = np.hstack((frame_x, stabilized_frame))
            current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES)) - 1
            cv2.imshow("Converting...", draw_progress_bar(concatenated_frame, current_frame/frame_count))

        frame_buffer = []
        
        prev_gray = gray.copy()
        prev_pts = curr_pts

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print("Perspective stabilization completed and video saved in:", output_path)