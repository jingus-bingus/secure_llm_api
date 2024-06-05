# Set Up
## Create hugging face account
- Create an account on [huggingface](https://huggingface.co/)
- Navigate to access tokens in settings and create a token with write access

## Download Model
- Request access to [Meta-Llama-3-8B-Instruct](https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct)

- Install git-lfs (linux command): 
`sudo apt install git-lfs`

- Once granted access to the model, clone repository: 
    - `git clone https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct`
    - Type your huggingface handle where it asks for a username 
    - Copy and paste the access token you created when asked for a password
    - This is a large download so don't worry if it seems to be stuck for a while


## Enable CUDA for pytorch
- Follow this guide to set up CUDA for pytorch: [geeksforgeeks CUDA setup](https://www.geeksforgeeks.org/how-to-set-up-and-run-cuda-operations-in-pytorch/)

## Download Packages
- This repository contains a file requirements.txt

- Navigate to the directory with this file

- `pip install -r requirements.txt`

- This command should install all packages necessary to run app.py

## Specify model path
- In app/app.py, the path to the model you downloaded must be specified in lines 16 and 17

```python
app.config['MODEL'] = LlamaForCausalLM.from_pretrained("your/path/to/model", quantization_config=bits_config)
app.config['TOKENIZER'] = AutoTokenizer.from_pretrained("your/path/to/model")
```

## Run API
- Navigate to the /app directory
- run ``python3 app.py``

## Run Example Front-end
- With the API still running, open another terminal and navigate to the root of the repository
- example_front.py is a simple terminal chat interface that uses the API to have a conversation with the large language model
- run ``python3 example_front.py``
- Type your message and press enter