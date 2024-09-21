# YouTube Quiz Generator 
Adaptively quiz a user on a YouTube video of their choice.

[![Demo](https://img.youtube.com/vi/YrBq8sr8Uqo/maxresdefault.jpg)](https://youtu.be/YrBq8sr8Uqo)

## Getting Started
Follow these guidelines to setup and run this project locally.
### Install
Create a conda environment 
```bash
conda create -n dev python=3.12
```
Install dependencies
```bash
pip install -r requirements.txt
```
Optional: Install `pipreqs` to seamlessly update dependencies in the future:
```bash
pip install pipreqs
pipreqs --force .
```

### Usage
1. Get a free API key at [Groq console](https://console.groq.com/keys)
2. Clone the repo:
    ```bash
    git clone https://github.com/hash-ir/yt-quiz-gen.git
    ```
3. Save the API key as an environment variable, ideally with the name `GROQ_API_KEY`
4. Run `main.py`
