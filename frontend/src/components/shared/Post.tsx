import React, { useState, useEffect } from "react";
import { Heart, MessageCircle, User, Trash2 } from "lucide-react";
import { formatDistanceToNowStrict } from "date-fns";
import { useNavigate } from "react-router-dom";

interface Comment {
  id: string;
  username: string;
  content: string;
  created_at: string;
}

interface PostProps {
  id: string;
  username: string;
  content: string;
  timestamp: string;
  likes: number;
  comments_count: number;
  image?: string;
}

const Post: React.FC<PostProps> = ({
  id,
  username,
  content,
  timestamp,
  likes: initialLikes,
  comments_count: initialCommentsCount,
  image,
}) => {
  const [showComments, setShowComments] = useState(false);
  const [comments, setComments] = useState<Comment[]>([]);
  const [newComment, setNewComment] = useState("");
  const [commentCount, setCommentCount] = useState(initialCommentsCount);
  const [isLiked, setIsLiked] = useState(false);
  const [likesCount, setLikesCount] = useState(initialLikes);
  const [avatarErrors, setAvatarErrors] = useState<Set<string>>(new Set());
  const navigate = useNavigate();
  const formattedTime = formatDistanceToNowStrict(new Date(timestamp)) + " ago";
  const currentUser = localStorage.getItem("username");

  useEffect(() => {
    const checkLikeStatus = async () => {
      try {
        const response = await fetch(
          `http://54.208.64.57:8001/api/posts/likes/${id}/check/`,
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem("access_token")}`,
            },
          }
        );
        if (response.ok) {
          const data = await response.json();
          setIsLiked(data.liked || false);
        }
      } catch (error) {
        console.error("Error checking like status:", error);
      }
    };

    if (localStorage.getItem("access_token")) {
      checkLikeStatus();
    }
  }, [id]);

  const handleLikeToggle = async () => {
    if (!localStorage.getItem("access_token")) {
      navigate("/login");
      return;
    }

    try {
      const response = await fetch(
        `http://54.208.64.57:8001/api/posts/likes/${id}/${
          isLiked ? "unlike" : "like"
        }/`,
        {
          method: isLiked ? "DELETE" : "POST",
          headers: {
            Authorization: `Bearer ${localStorage.getItem("access_token")}`,
          },
        }
      );

      if (response.ok) {
        setIsLiked(!isLiked);
        setLikesCount((prevCount) => (isLiked ? prevCount - 1 : prevCount + 1));
      }
    } catch (error) {
      console.error("Error toggling like:", error);
    }
  };

  const fetchComments = async () => {
    try {
      const response = await fetch(
        `http://54.208.64.57:8001/api/posts/comments/by_post/${id}/`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("access_token")}`,
          },
        }
      );
      if (response.ok) {
        const data = await response.json();
        setComments(data.results || []);
      }
    } catch (error) {
      console.error("Error fetching comments:", error);
    }
  };

  useEffect(() => {
    if (showComments) {
      fetchComments();
    }
  }, [showComments, id]);

  const handleAddComment = async () => {
    if (!newComment.trim()) return;

    try {
      const response = await fetch(
        `http://54.208.64.57:8001/api/posts/comments/add/${id}/`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${localStorage.getItem("access_token")}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ content: newComment }),
        }
      );

      if (response.ok) {
        const comment = await response.json();
        setComments((prevComments) => [comment, ...prevComments]);
        setNewComment("");
        setCommentCount((prev) => prev + 1);
      }
    } catch (error) {
      console.error("Error adding comment:", error);
    }
  };

  const handleDeleteComment = async (commentId: string) => {
    try {
      const response = await fetch(
        `http://54.208.64.57:8001/api/posts/comments/${commentId}/delete/`,
        {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${localStorage.getItem("access_token")}`,
          },
        }
      );

      if (response.ok) {
        setComments((prevComments) =>
          prevComments.filter((comment) => comment.id !== commentId)
        );
        setCommentCount((prev) => prev - 1);
      }
    } catch (error) {
      console.error("Error deleting comment:", error);
    }
  };

  const navigateToProfile = (username: string) => {
    navigate(`/profile/${username}`);
  };

  const handleAvatarError = (username: string) => {
    setAvatarErrors((prev) => new Set([...prev, username]));
  };

  const renderAvatar = (username: string, size: "small" | "large") => {
    const dimensions = size === "small" ? "w-8 h-8" : "w-10 h-10";
    return avatarErrors.has(username) ? (
      <div
        className={`${dimensions} rounded-full bg-gray-200 flex items-center justify-center`}
      >
        <User className={size === "small" ? "w-4 h-4" : "w-6 h-6"} />
      </div>
    ) : (
      <img
        src={`/images/avatar/${username}.jpg`}
        alt={`${username}'s Avatar`}
        className={`${dimensions} rounded-full`}
        onError={() => handleAvatarError(username)}
      />
    );
  };

  return (
    <div className="bg-white rounded-lg shadow-md">
      <div className="p-4">
        <div className="flex items-start">
          <div
            className="cursor-pointer mr-4"
            onClick={() => navigateToProfile(username)}
          >
            {renderAvatar(username, "large")}
          </div>
          <div className="flex-1">
            <div className="flex items-center justify-between">
              <h3
                className="font-semibold cursor-pointer hover:underline"
                onClick={() => navigateToProfile(username)}
              >
                {username}
              </h3>
              <span className="text-sm text-gray-500">{formattedTime}</span>
            </div>
            <p className="mt-2">{content}</p>
            {image && image.trim() !== "" && (
              <div className="mt-4">
                <img
                  src={image}
                  alt="Post image"
                  className="w-full h-auto rounded"
                />
              </div>
            )}
            <div className="flex items-center mt-4 space-x-6 text-gray-500">
              <button
                className="flex items-center space-x-2 hover:text-blue-500"
                onClick={() => setShowComments(!showComments)}
              >
                <MessageCircle size={16} />
                <span>{commentCount}</span>
              </button>
              <button
                className={`flex items-center space-x-2 hover:text-red-500 ${
                  isLiked ? "text-red-500" : ""
                }`}
                onClick={handleLikeToggle}
              >
                <Heart size={16} fill={isLiked ? "currentColor" : "none"} />
                <span>{likesCount}</span>
              </button>
            </div>

            {showComments && (
              <div className="mt-4 space-y-4">
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={newComment}
                    onChange={(e) => setNewComment(e.target.value)}
                    placeholder="Write a comment..."
                    className="flex-1 px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    onKeyPress={(e) => {
                      if (e.key === "Enter") {
                        handleAddComment();
                      }
                    }}
                  />
                  <button
                    onClick={handleAddComment}
                    className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
                  >
                    Comment
                  </button>
                </div>

                <div className="space-y-3">
                  {comments.map((comment) => (
                    <div
                      key={comment.id}
                      className="flex items-start space-x-3 bg-gray-50 p-3 rounded-lg"
                    >
                      <div
                        className="cursor-pointer"
                        onClick={() => navigateToProfile(comment.username)}
                      >
                        {renderAvatar(comment.username, "small")}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-start justify-between">
                          <div
                            className="font-semibold cursor-pointer hover:underline"
                            onClick={() => navigateToProfile(comment.username)}
                          >
                            {comment.username}
                          </div>
                          {currentUser === comment.username && (
                            <button
                              onClick={() => handleDeleteComment(comment.id)}
                              className="text-gray-400 hover:text-red-500 transition-colors"
                              title="Delete comment"
                            >
                              <Trash2 size={16} />
                            </button>
                          )}
                        </div>
                        <p className="text-sm">{comment.content}</p>
                        <span className="text-xs text-gray-500">
                          {formatDistanceToNowStrict(
                            new Date(comment.created_at)
                          )}{" "}
                          ago
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Post;
