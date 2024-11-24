import React from "react";
import { Card } from "@/components/ui/card";
import { Avatar, AvatarImage } from "@/components/ui/avatar";
import { Heart, MessageCircle, Repeat } from "lucide-react";
import { formatDistanceToNowStrict } from "date-fns";

interface PostProps {
  username: string;
  avatar: string;
  content: string;
  timestamp: string;
  comments: number;
  retweets: number;
  likes: number;
  images: string[];
}

const Post: React.FC<PostProps> = ({
  username,
  avatar,
  content,
  timestamp,
  comments,
  retweets,
  likes,
  images,
}) => {
  const formattedTime: string =
    formatDistanceToNowStrict(new Date(timestamp)) + " ago";

  return (
    <Card>
      <div className="p-4">
        <div className="flex items-start">
          <Avatar className="mr-4">
            <AvatarImage src={avatar} alt={`${username}'s Avatar`} />
          </Avatar>
          <div className="flex-1">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold">{username}</h3>
              <span className="text-sm text-gray-500">{formattedTime}</span>
            </div>
            <p className="mt-2">{content}</p>
            {images.length > 0 && (
              <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-2">
                {images.map((img, index) => (
                  <img
                    key={index}
                    src={img}
                    alt={`Post image ${index + 1}`}
                    className="w-full h-auto rounded"
                  />
                ))}
              </div>
            )}
            <div className="flex items-center mt-4 space-x-6 text-gray-500">
              <button className="flex items-center space-x-2 hover:text-blue-500">
                <MessageCircle size={16} />
                <span>{comments}</span>
              </button>
              <button className="flex items-center space-x-2 hover:text-green-500">
                <Repeat size={16} />
                <span>{retweets}</span>
              </button>
              <button className="flex items-center space-x-2 hover:text-red-500">
                <Heart size={16} />
                <span>{likes}</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
};

export default Post;
