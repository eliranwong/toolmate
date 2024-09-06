# Google API Setup

LetMeDoIt integrates the following Google API services:

* Vertex AI [Gemini Pro / Gemini Pro Vision / PaLM 2 / Codey]
* Cloud Speech-to-Text
* Cloud Text-to-Speech

Remarks: It works even in EU / UK. At the time of writing, web-based Google AI Studio is not accessible in [EU / UK / some other regions](https://ai.google.dev/available_regions#available_regions).  As this python package is based on Google Vertex AI APIs, there is no such restriction.

# Set up your Google Cloud Platform project

1. Go to https://console.cloud.google.com/

![new_project](https://github.com/eliranwong/letmedoit/assets/25262722/e3c3a5f0-9155-414b-816a-b10bf7cfa839)

2. Either "Select a project" or create "NEW PROJECT", enter, e.g.:

Project name: letmedoitai

![project_name](https://github.com/eliranwong/letmedoit/assets/25262722/c9d99cf2-1e2f-410a-966e-cb62e3bd2867)

3. Set up billing information

MENU > Billing > Payment method

4. Set up service account

MENU > MORE PRODUCTS > IAM & ADMIN > Service Accounts

![menu_service_account](https://github.com/eliranwong/letmedoit/assets/25262722/2ad81bb0-53c0-4958-b44c-20b00ab161a9)

Create service account, e.g.:

* Service account name: letmedoitai

* Service account ID: letmedoitai

* Service account description: letmedoitai

Click "CREATE AND CONTINUE"

![create_service_account_button](https://github.com/eliranwong/letmedoit/assets/25262722/47a3647f-ad36-4c1e-acae-9d40127e6379)

![service_account_details](https://github.com/eliranwong/letmedoit/assets/25262722/5445d6e9-c609-4dd9-93c3-e9ce9d6efe73)

* Select role > Owner > CONTINUE > DONE

![role_owner](https://github.com/eliranwong/letmedoit/assets/25262722/1cb0db0d-9971-4ae4-994b-011708cd62e9)

5. Download API key in JSON format

Right next to the created service account, select the 3-dot action button > Manage keys

![manage_keys](https://github.com/eliranwong/letmedoit/assets/25262722/73d32cc9-8fc0-4f2f-93bd-fa1acb42060a)

ADD KEY > Create new key

![create_new_key](https://github.com/eliranwong/letmedoit/assets/25262722/5ac459ad-6df1-4bb3-b2fc-88566fe73a53)

Select JSON format and automatically download the file

![json_format](https://github.com/eliranwong/letmedoit/assets/25262722/5fdf3d03-e263-45d6-8526-44c454450060)

# Enable APIs in Google Console

## Gemini Pro

1. Go to https://console.cloud.google.com/vertex-ai

2. Click "ENABLE ALL RECOMMENDATED APIS"

3. Copy the JSON file, downloaded in the previous step, to directory "\~/letmedoit/" and rename it as "credentials_google_cloud.json"

![gemini_pro_api](https://github.com/eliranwong/letmedoit/assets/25262722/78b2f78c-2823-45ad-9645-d924c07e4ef7)

![service_enabled](https://github.com/eliranwong/letmedoit/assets/25262722/eb9e9fa7-873c-48b8-8249-dce9a9812b31)

## Cloud Speech-to-text

1. Go to https://cloud.google.com/speech-to-text

2. Click "ENABLE"

3. Copy the JSON file, downloaded in the previous step, to directory "\~/letmedoit/" and rename it as "credentials_google_cloud.json"

## Cloud Text-to-speech

1. Go to https://console.cloud.google.com/speech/text-to-speech

2. Click "ENABLE"

3. Copy the JSON file, downloaded in the previous step, to directory "\~/letmedoit/" and rename it as "credentials_google_cloud.json"

![enable_tts](https://github.com/eliranwong/letmedoit/assets/25262722/8c61023f-f774-467a-b5dc-ae1cb92702d4)

Remarks:

* The "~" in the copied path denotes user home directory

* Copy to "\~/myhand/", "\~/taskwiz/", "\~/cybertask/" if you also install packages myhand, taskwiz, cyber task

* In case you install our python package googleaistudio, copied the json file to "\~/googleaistudio/credentials_googleaistudio.json"

# Enable Google API Service in LetMeDoIt

You can enable none / some / all supported Google API Service in LetMeDoIt AI.

Select "Change Google API Service" from action menu and select the service that you want from the dialog:

<img width="857" alt="change_google_api_service" src="https://github.com/eliranwong/letmedoit/assets/25262722/7614ec71-d3c1-4010-a55f-a2d3a08b72b8">

# Integration with LetMeDoIt Plugins

https://github.com/eliranwong/letmedoit/wiki/Integration-with-Google-AI-Tools

# Information about Pricing

Please refer to the following information about pricing, charged by Google, depending on your usage.

## Gemini Pro

Reference:

* https://cloud.google.com/vertex-ai/pricing

For example, pricing for Gemini Pro:

With the Multimodal models in Vertex AI, you can input either text or media (images, video). Text input is charged by every 1,000 characters of input (prompt) and every 1,000 characters of output (response). Characters are counted by UTF-8 code points and white space is excluded from the count. Prediction requests that lead to filtered responses are charged for the input only. At the end of each billing cycle, fractions of one cent ($0.01) are rounded to one cent. Media input is charged per image or per second (video).

At the time of writing, Google is offering a limited-time opportunity for developers to try Gemini Pro for free on Vertex AI until January 15, 2024.

## Speech-to-text

Reference: https://cloud.google.com/speech-to-text

## Text-to-speech

Reference: https://console.cloud.google.com/speech/text-to-speech

Text-to-Speech is priced based on the number of characters sent to the service to be synthesized into audio each month. The first 1 million characters for WaveNet voices are free each month. For Standard (non-WaveNet) voices, the first 4 million characters are free each month. After the free tier has been reached, Text-to-Speech is priced per 1 million characters of text processed.
