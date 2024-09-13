import os
import requests
import urllib.parse

# API 的基础 URL
base_url = "https://douyin.wtf/api/douyin/web/fetch_user_post_videos"

# 用户sec_user_id与保存目录的映射
users = {
    "liuxinyi": "MS4wLjABAAAA9nKMV9HCdu7y7HmVNp_mBuF0lx5YgZZn1mbfDExpZkQ",
    "panyue": "MS4wLjABAAAA7Pyg6a9E5OBKgpGYBcghgdbU6szhucTLKW0vDAQsfAmC9HuJKZ4uBmbvqudCqlni"
}

# 默认游标和视频数量
max_cursor = 0
count = 20

def fetch_user_videos(sec_user_id, max_cursor=0, count=20):
    # URL 编码 sec_user_id
    encoded_sec_user_id = urllib.parse.quote(sec_user_id)
    
    # 构建请求参数
    params = {
        "sec_user_id": encoded_sec_user_id,
        "max_cursor": max_cursor,
        "count": count
    }
    
    # 发送 GET 请求
    response = requests.get(base_url, params=params)
    
    # 检查请求状态
    if response.status_code == 200:
        try:
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error decoding JSON response for user {sec_user_id}: {e}")
            return None
    else:
        print(f"Failed to fetch data: {response.status_code} for user {sec_user_id}")
        return None

def download_video(video_url, save_path):
    response = requests.get(video_url, stream=True)
    if response.status_code == 200:
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print(f"Downloaded {save_path}")
    else:
        print(f"Failed to download video from {video_url}")

def main():
    # 遍历每个用户
    for folder, sec_user_id in users.items():
        # 创建对应用户的文件夹
        os.makedirs(f'videos/{folder}', exist_ok=True)
        
        # 获取用户作品数据
        user_videos_data = fetch_user_videos(sec_user_id, max_cursor, count)
        
        # 打印完整的响应数据，用于调试
        print(f"Response for {folder}: {user_videos_data}")
        
        if user_videos_data:
            # 确认 'aweme_list' 键是否存在
            if 'aweme_list' in user_videos_data:
                for idx, video in enumerate(user_videos_data['aweme_list']):
                    # 获取视频信息
                    video_url = video['video']['play_addr']['url_list'][0]
                    description = video['desc']
                    video_id = video['aweme_id']
                    
                    # 构建保存路径
                    save_path = f"videos/{folder}/{video_id}.mp4"
                    
                    # 下载视频
                    download_video(video_url, save_path)
            else:
                print(f"Key 'aweme_list' not found in response for {folder}")
            
            # 获取下一页游标
            next_cursor = user_videos_data.get('max_cursor', 0)
            print(f"下一页的游标: {next_cursor} for user {folder}")
        else:
            print(f"未能获取到用户 {folder} 的作品数据")

if __name__ == "__main__":
    main()
