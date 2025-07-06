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
  new_larger_dimension=140
  new_smaller_dimension=$((140 * smaller_dimension / larger_dimension))
  if [ "${dimensions[1]}" -ge "${dimensions[2]}" ]; then
    dimensions2="${new_larger_dimension}x${new_smaller_dimension}"
  else
    dimensions2="${new_smaller_dimension}x${new_larger_dimension}"
  fi

  # Resize the image using ImageMagick
  convert "$input_image" -resize "$dimensions2" -format bmp "$output_image"

  echo "Image resized and converted to PNG: $output_image"
}

resize_image_stick() {
  if [ $# -ne 2 ]; then
      echo "Usage: resize_image input_image output_image"
      return 1
  fi
  input_image="$1"
  output_image="$2"
  dimensions=($(identify -format "%w %h" "$input_image"))

  width="${dimensions[1]}"
  height="${dimensions[2]}"
  new_width=140
  new_height=$((new_width * width / height + 1))

  echo ${height} ${width}
  echo ${new_height} ${new_width}
  convert "${input_image}" -rotate 90 -resize "${new_width}x${new_height}" -format bmp "${output_image}"
  echo "Image resized and converted for Timo's light stick: ${output_image}"
}
