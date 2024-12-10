import React, { useState, useRef } from "react";
import { Card } from "../ui/card";
import { Button } from "../ui/button";
import { ImageIcon } from "lucide-react";

interface CreatePostProps {
  onPostCreated?: () => void;
}

const CreatePost: React.FC<CreatePostProps> = ({ onPostCreated }) => {
  const [content, setContent] = useState("");
  const [image, setImage] = useState<File | null>(null);
  const [hashtags, setHashtags] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isGeneratingHashtags, setIsGeneratingHashtags] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
  //   if (e.target.files && e.target.files.length > 0) {
  //     setImage(e.target.files[0]);
  //   }
  // };

  const generateHashtags = async () => {
    setIsGeneratingHashtags(true);
    setError(null);

    try {
      const token = localStorage.getItem("access_token");
      if (!token) {
        throw new Error("Authentication required");
      }

      const formData = new FormData();
      formData.append("text", content);
      if (image) {
        formData.append("image", image);
      }

      const response = await fetch(
        "http://54.208.64.57:8001/api/posts/hashtags/generate/generate/",
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
          credentials: "include",
          body: formData,
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || "Failed to generate hashtags");
      }

      const { hashtags: generatedHashtags } = await response.json();
      setHashtags(generatedHashtags.map((tag: string) => `${tag}`));
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to generate hashtags"
      );
    } finally {
      setIsGeneratingHashtags(false);
    }
  };

  const removeImage = () => {
    setImage(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append("content", content);

      // Append each image to formData
      if (image) {
        formData.append("image", image);
      }

      // Append each hashtag individually to formData
      hashtags.forEach((tag) => {
        formData.append("hashtags", tag);
      });

      const token = localStorage.getItem("access_token");
      if (!token) {
        throw new Error("Authentication required");
      }

      const response = await fetch(
        "http://54.208.64.57:8001/api/posts/posts/",
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
          credentials: "include",
          body: formData,
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || "Failed to create post");
      }

      // Reset form
      setContent("");
      setImage(null);
      setHashtags([]);

      // Notify parent component
      if (onPostCreated) {
        onPostCreated();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="p-4">
      <form onSubmit={handleSubmit}>
        {/* Content Input */}
        <textarea
          className="w-full p-2 border rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="What's happening?"
          rows={3}
          value={content}
          onChange={(e) => setContent(e.target.value)}
          maxLength={280}
          required
        />

        {/* Action Buttons */}
        <div className="mt-2 flex items-center space-x-2">
          <Button
            type="button"
            variant="outline"
            onClick={generateHashtags}
            disabled={isGeneratingHashtags || !content.trim()}
          >
            {isGeneratingHashtags ? "Generating..." : "Generate Hashtags"}
          </Button>

          <Button
            type="submit"
            disabled={isLoading || !content.trim()}
            className="bg-blue-500 text-white px-4 py-2 rounded-full hover:bg-blue-600 disabled:opacity-50"
          >
            {isLoading ? "Posting..." : "Post"}
          </Button>

          <Button
            type="button"
            variant="ghost"
            size="icon"
            onClick={() => fileInputRef.current?.click()}
            className="ml-auto"
          >
            <ImageIcon className="h-5 w-5" />
          </Button>
        </div>

        {/* Display Hashtags */}
        {hashtags.length > 0 && (
          <div className="mt-2">
            <div className="flex flex-wrap gap-2">
              {hashtags.map((tag, index) => (
                <span
                  key={index}
                  className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-sm"
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
        )}

        {image && (
          <div className="mt-2 relative">
            <img
              src={URL.createObjectURL(image)}
              alt="Upload preview"
              className="w-full h-32 object-cover rounded"
            />
            <button
              type="button"
              className="absolute top-1 right-1 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center"
              onClick={removeImage}
            >
              ×
            </button>
          </div>
        )}

        {error && <div className="mt-2 text-red-500 text-sm">{error}</div>}
      </form>
    </Card>
  );
};

export default CreatePost;
