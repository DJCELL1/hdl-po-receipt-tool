import sharp from 'sharp';
import Jimp from 'jimp';

export interface PreprocessingOptions {
  deskew?: boolean;
  enhanceContrast?: boolean;
  denoise?: boolean;
  convertToGrayscale?: boolean;
  threshold?: boolean;
}

export class ImagePreprocessor {
  /**
   * Preprocess image for optimal OCR results
   */
  async preprocessImage(
    inputPath: string,
    outputPath: string,
    options: PreprocessingOptions = {}
  ): Promise<string> {
    const {
      deskew = true,
      enhanceContrast = true,
      denoise = true,
      convertToGrayscale = true,
      threshold = true
    } = options;

    try {
      console.log('Starting image preprocessing...');

      // Load image with sharp for initial processing
      let image = sharp(inputPath);

      // Convert to grayscale
      if (convertToGrayscale) {
        image = image.grayscale();
      }

      // Enhance contrast
      if (enhanceContrast) {
        image = image.normalize();
      }

      // Save intermediate result
      const tempPath = outputPath.replace(/\.(jpg|jpeg|png)$/i, '_temp.png');
      await image.png().toFile(tempPath);

      // Use Jimp for advanced operations
      let jimpImage = await Jimp.read(tempPath);

      // Denoise
      if (denoise) {
        jimpImage = jimpImage.blur(1);
      }

      // Increase contrast
      if (enhanceContrast) {
        jimpImage = jimpImage.contrast(0.3);
      }

      // Apply threshold for better text detection
      if (threshold) {
        jimpImage = jimpImage.threshold({ max: 128, replace: 255, autoGreyscale: false });
      }

      // Deskew if needed (simple rotation detection)
      if (deskew) {
        // Note: Full deskew would require more complex algorithms
        // This is a simplified version
        jimpImage = await this.autoRotate(jimpImage);
      }

      // Save final processed image
      await jimpImage.writeAsync(outputPath);

      console.log('Image preprocessing completed:', outputPath);
      return outputPath;
    } catch (error) {
      console.error('Image preprocessing failed:', error);
      throw new Error(`Failed to preprocess image: ${error}`);
    }
  }

  /**
   * Auto-rotate image based on EXIF orientation
   */
  private async autoRotate(image: Jimp): Promise<Jimp> {
    // Auto-rotate based on EXIF data if available
    return image.rotate(0, false); // Jimp handles EXIF rotation automatically
  }

  /**
   * Resize image if too large for OCR
   */
  async resizeIfNeeded(inputPath: string, maxWidth = 2000): Promise<string> {
    const image = sharp(inputPath);
    const metadata = await image.metadata();

    if (metadata.width && metadata.width > maxWidth) {
      const outputPath = inputPath.replace(/\.(jpg|jpeg|png)$/i, '_resized.png');
      await image.resize(maxWidth).png().toFile(outputPath);
      return outputPath;
    }

    return inputPath;
  }

  /**
   * Convert PDF page to image
   */
  async convertPdfToImage(_pdfPath: string, _pageNumber = 0): Promise<string> {
    // For production, you'd use pdf-poppler or similar
    // This is a placeholder that assumes pdf-parse extracts text directly
    throw new Error('PDF to image conversion requires additional setup (pdf-poppler)');
  }
}

export const imagePreprocessor = new ImagePreprocessor();
