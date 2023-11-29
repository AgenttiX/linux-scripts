#!/usr/bin/env zsh

resize_image() {
  if [ $# -ne 2 ]; then
      echo "Usage: resize_image input_image output_image"
      return 1
  fi

  input_image="$1"
  output_image="$2"

  # Get the dimensions of the input image
  dimensions=($(identify -format "%w %h" "$input_image"))

  # Determine the larger dimension
  if [ "${dimensions[1]}" -ge "${dimensions[2]}" ]; then
      larger_dimension="${dimensions[1]}"
      smaller_dimension="${dimensions[2]}"
  else
      larger_dimension="${dimensions[2]}"
      smaller_dimension="${dimensions[1]}"
  fi

  # Calculate the new dimensions while preserving the aspect ratio
  new_larger_dimension=512
  new_smaller_dimension=$((512 * smaller_dimension / larger_dimension))
  if [ "${dimensions[1]}" -ge "${dimensions[2]}" ]; then
    dimensions2="${new_larger_dimension}x${new_smaller_dimension}"
  else
    dimensions2="${new_smaller_dimension}x${new_larger_dimension}"
  fi

  # Resize the image using ImageMagick
  convert "$input_image" -resize "$dimensions2" -format png "$output_image"

  echo "Image resized and converted to PNG: $output_image"
}
