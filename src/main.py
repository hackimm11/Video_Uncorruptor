from Uncorruptor_class import Uncorruptor

if __name__ == "__main__":

    vid_in = "../input/corrupted_video.mp4"
    vid_out1 = "../output/final_video_1.mp4"
    vid_out2 = "../output/final_video_2.mp4"

    Uncorruptor = Uncorruptor(vid_in, vid_out1, vid_out2)
    Uncorruptor.uncorrupted_vids()
