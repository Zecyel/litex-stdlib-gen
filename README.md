# litex-testset
A testset of litexlang

## Prepare the data

The `prompt/` folder is gitignored. Generate by running the following code: (Don't forget to clone golitex and litex-tutorial repos!)

```bash
python autogen/dump_folder.py --path ../golitex/examples/comprehensive_examples/ -o ./prompt/examples.txt
python autogen/dump_folder.py --path ../litex-tutorial/Tutorial/ -o ./prompt/tutor.txt
```

Postscript: If you don't like `../litex-tutorial/Tutorial/.order` file, you can manually delete it from `./prompt/tutor.txt`.

## Run the code

```bash
export OPENAI_API_KEY=你的大模型密钥
export OPENAI_BASE_URL=大模型服务商的base url，注意需要带上/v1/chat/completions之类的后缀
cd autogen && python3 gen.py
```
