def open_RTC_violence(socketio, vc):
    # current_vc = vc
    # max_v = 5
    # v_count = 0
    frame_number = 0
    frames_list = []
    # start_time = None
    # isRecording = False
    # width = int(vc.get(cv2.CAP_PROP_FRAME_WIDTH))
    # height = int(vc.get(cv2.CAP_PROP_FRAME_HEIGHT))

    while True:
        ret, frame = vc.read()
        frame_number += 1
        if not ret:
            break
        # img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # img = cv2.resize(img, (128, 128)).astype("float32")
        # img = img.reshape(128, 128, 3) / 255
        # predictions = model.predict(np.expand_dims(img, axis=0), verbose=0)
        # preds = predictions > 0.5

        # 1
        # if len(frames_list) < 5:
        #     frames_list.append(preds[0][0])
        # 1
        # else:
        #     frames_list.pop(0)
        #     frames_list.append(preds[0][0])

        # 1
        # if preds and v_count != max_v:
            # v_count += 1

        # 1
        # if not isRecording and max_v == v_count:
        #     file_name = uuid.uuid4()
        #     ct = current_datetime()
        #     print("file_name: ", file_name)
        #     print("ct: ", ct)
        #     # save warning video file to /static/warning
        #     writer = cv2.VideoWriter(
        #         f'{warning_path}{file_name}.mp4', cv2.VideoWriter_fourcc(*'DIVX'), 5, (width, height))
        #     print("warning video saved successfully")
        #     # save the video to warnings table to db
        #     data = {
        #         "status": "Violence",
        #         "video_name": f"{file_name}.mp4",
        #         "date": ct,
        #     }
        #     print(data)

        #     warn = WarningModel(**data)
        #     print(warn)
        #     try:
        #         warn.save_to_db()
        #         print("warning saved to db successfully")

        #     except Exception as e:
        #         print(e)

        #     # FR_thread = FaceRecognition(f'{file_name}.mp4,')
        #     print("Initiate FaceRecognition successfully")
        #     start_time = time.time()
        #     isRecording = True

        # # 1
        # if isRecording:
            # 2
            if time.time() - start_time > 10:
                print(frames_list)
                # 3
                if np.sum(frames_list) > 1:
                    start_time = time.time()
                    writer.write(frame)
                # 3
                else:
                    writer.release()
                    v_count = 0
                    isRecording = False
                    # FR_thread.run(ct)
                    
            # 2
            else:
                writer.write(frame)

        # cv2.putText(frame, f'Violence : {preds[0][0]}', (10, 50),
        #             cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, 2)

        # frame = cv2.imencode('.jpg', frame)[1]
        # frame = frame.tobytes()
        # socketio.emit('rtc', frame)
        # socketio.sleep(0)
        if len(frames_list) > 5:
            break

    vc.release()


           # k = cv2.waitKey(1)
        # if ord('q') == k:
        #     break