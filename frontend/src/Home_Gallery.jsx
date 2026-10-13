import { useState } from "react";

function HomeImageGallery({ images }) {
  // Keeps track of which image is currently being displayed
  const [currentImage, setCurrentImage] = useState(0);

  // If there are no images, don't display the gallery
  if (!images || images.length === 0) {
    return null;
  }

  // Move to the next image
  const nextImage = () => {
    setCurrentImage((current) => {
      if (current === images.length - 1) {
        return 0;
      }

      return current + 1;
    });
  };

  // Move to the previous image
  const previousImage = () => {
    setCurrentImage((current) => {
      if (current === 0) {
        return images.length - 1;
      }

      return current - 1;
    });
  };

  return (
    <div className="image-gallery">

      <img
        className="home-image"
        src={`https://cdn.repliers.io/${images[currentImage]}?class=medium`}
        alt={`Home ${currentImage + 1}`}
      />

      <button
        className="gallery-button left-button"
        onClick={previousImage}
      >
        ‹
      </button>

      <button
        className="gallery-button right-button"
        onClick={nextImage}
      >
        ›
      </button>

      <div className="image-counter">
        {currentImage + 1} / {images.length}
      </div>

    </div>
  );
}

export default HomeImageGallery;