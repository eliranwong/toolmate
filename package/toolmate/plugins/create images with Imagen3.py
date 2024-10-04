"""
ToolMate AI Plugin - create images

generate images with model "Google Imagen 3"

[TOOL_CALL]
"""

if not config.isTermux:

  from toolmate import config, print3, getCurrentDateTime
  import os, subprocess
  from pathlib import Path

  import vertexai
  from vertexai.preview.vision_models import ImageGenerationModel


  def create_image_imagen3(function_args):
      def openImageFile(imageFile):
          if config.terminalEnableTermuxAPI:
              getCliOutput(f"termux-share {imageFile}")
          else:
              cli = f"{config.open} {imageFile}"
              #os.system(cli)
              subprocess.Popen(cli, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

      prompt = function_args.get("prompt") # required

      if os.environ["GOOGLE_APPLICATION_CREDENTIALS"] and "Vertex AI" in config.enabledGoogleAPIs:
          # initiation
          vertexai.init()
      else:
          print("Vertex AI is not enabled!")
          print("Read https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Google%20Cloud%20Service%20Credential%20Setup.md for setting up Google API.")
          return "[INVALID]"
      
      generation_model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-001")

      # reference: https://cloud.google.com/blog/products/ai-machine-learning/a-developers-guide-to-imagen-3-on-vertex-ai?e=0?utm_source%3Dlinkedin
      """Generates images from text prompt.

      Args:
          prompt: Text prompt for the image.
          negative_prompt: A description of what you want to omit in the generated
            images.
          number_of_images: Number of images to generate. Range: 1..8.
          width: Width of the image. One of the sizes must be 256 or 1024.
          height: Height of the image. One of the sizes must be 256 or 1024.
          aspect_ratio: Aspect ratio for the image. Supported values are:
              * 1:1 - Square image
              * 9:16 - Portait image
              * 16:9 - Landscape image
              * 4:3 - Landscape, desktop ratio.
              * 3:4 - Portrait, desktop ratio
          guidance_scale: Controls the strength of the prompt. Suggested values
            are - * 0-9 (low strength) * 10-20 (medium strength) * 21+ (high
            strength)
          seed: Image generation random seed.
          base_image: Base image to use for the image generation.
          mask: Mask for the base image.
          edit_mode: Describes the editing mode for the request. Supported values
            are - * inpainting-insert: fills the mask area based on the text
            prompt (requires mask and text) * inpainting-remove: removes the
            object(s) in the mask area. (requires mask)
              * outpainting: extend the image based on the mask area. (Requires
                mask) * product-image: Changes the background for the predominant
                product or subject in the image
          mask_mode: Solicits generation of the mask (v/s providing mask as an
            input). Supported values are:
              * background: Automatically generates a mask for all regions except
                the primary subject(s) of the image
              * foreground: Automatically generates a mask for the primary
                subjects(s) of the image.
              * semantic: Segment one or more of the segmentation classes using
                class ID
          segmentation_classes: List of class IDs for segmentation. Max of 5 IDs
          mask_dilation: Defines the dilation percentage of the mask provided.
            Float between 0 and 1. Defaults to 0.03
          product_position: Defines whether the product should stay fixed or be
            repositioned. Supported Values:
              * fixed: Fixed position
              * reposition: Can be moved (default)
          output_mime_type: Which image format should the output be saved as.
            Supported values: * image/png: Save as a PNG image * image/jpeg: Save
            as a JPEG image
          compression_quality: Level of compression if the output mime type is
            selected to be image/jpeg. Float between 0 to 100
          language: Language of the text prompt for the image. Default: None.
            Supported values are `"en"` for English, `"hi"` for Hindi, `"ja"` for
            Japanese, `"ko"` for Korean, and `"auto"` for automatic language
            detection.
          output_gcs_uri: Google Cloud Storage uri to store the generated images.
          add_watermark: Add a watermark to the generated image
          safety_filter_level: Adds a filter level to Safety filtering. Supported
            values are: * "block_most" : Strongest filtering level, most strict
            blocking * "block_some" : Block some problematic prompts and responses
            * "block_few" : Block fewer problematic prompts and responses *
            "block_fewest" : Block very few problematic prompts and responses
          person_generation: Allow generation of people by the model Supported
            values are: * "dont_allow" : Block generation of people *
            "allow_adult" : Generate adults, but not children * "allow_all" :
            Generate adults and children

      Returns:
          An `ImageGenerationResponse` object.
      """

      image = generation_model.generate_images(
          prompt=prompt,
          number_of_images=1,
          aspect_ratio="1:1",
          safety_filter_level="block_few", # Literal["block_most", "block_some", "block_few", "block_fewest"]
          person_generation="allow_adult", # Literal["dont_allow", "allow_adult", "allow_all"]
      )
      #print(dir(image[0])) # ['__annotations__', '__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_as_base64_string', '_blob', '_gcs_uri', '_generation_parameters', '_image_bytes', '_loaded_bytes', '_loaded_image', '_mime_type', '_pil_image', '_size', 'generation_parameters', 'load_from_file', 'save', 'show']
      
      # image file path
      folder = os.path.join(config.localStorage, "images")
      Path(folder).mkdir(parents=True, exist_ok=True)
      imageFile = os.path.join(folder, f"{getCurrentDateTime()}.png")
      # save image
      image[0].save(imageFile)
      message = f"Saved image: {imageFile}"
      config.toolTextOutput = message
      print3(message)
      # open image
      openImageFile(imageFile)
      return ""

  functionSignature = {
      "examples": [
          "generate image",
          "create image",
      ],
      "name": "create_image_imagen3",
      "description": "Create an image with Imagen 3",
      "parameters": {
          "type": "object",
          "properties": {
              "prompt": {
                  "type": "string",
                  "description": "Description of the image in as much detail as possible",
              },
          },
          "required": ["prompt"],
      },
  }

  config.addFunctionCall(signature=functionSignature, method=create_image_imagen3)