"""Batch Evaluation for MCQ - AgentFlow Simple"""
import socket
socket.setdefaulttimeout(120)

import asyncio
import argparse
import os
import sys
import yaml
import re

import logging
logging.basicConfig(level=logging.WARNING)

from pathlib import Path
import pandas as pd
from tqdm.asyncio import tqdm_asyncio

from graph.graph import BiologicalResearcher



def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--input_path",
        type=str,
        help="Input CSV file path containing questions"
    )
    parser.add_argument(
        "-o", "--output_path",
        type=str,
        help="Output CSV file path for results"
    )
    parser.add_argument(
        "-c", "--config_path", 
        type=str,
        help="Configuration file path"
    )
    parser.add_argument(
        "-e", "--only_eval",
        action="store_true",
        help="Only evaluate existing results without processing"
    )
    
    return parser.parse_args()

def process_results(df, results, query_type):
    if query_type == "MCQ" or query_type == "SCQ":
        options, reasons, conversations = [], [], []
        for answer, conversation in results:
            conversations.append(conversation)
            match = re.search(r'Answer:\s*([A-Z]+)', answer)
            if match:
                options.append(match.group(1))
            else:
                options.append("")
            reason = re.search(r'Reason:\s*(.*)', answer, re.DOTALL)
            if reason:
                reasons.append(reason.group(1).strip())
            else:
                reasons.append("")
        df['response'] = options
        df["reason"] = reasons
        df['conversation'] = conversations
        df['accuracy'] = (df['answer'] == df['response']).astype(int)
    elif query_type == "QA" or query_type == "H":
        answer, conversation = zip(*results)
        df['response'] = list(answer)
        df['conversation'] = list(conversation)
        import evaluate
        rouge = evaluate.load("rouge")
        metrics = rouge.compute(
            predictions=df["answer"].to_list(), references=df["response"].to_list(), 
            use_stemmer=True, use_aggregator=False,
            # rouge_types=["rougeL"],
        )
        for k, v in metrics.items():
            df[k] = v
    else:
        raise ValueError(f"Unsupported query type: {query_type}")

    return df

async def process_batch_async(config, batch_questions):
    researcher = BiologicalResearcher(config)
    tasks = [researcher.research(question, return_conversation=True) for question in batch_questions]
    results = await tqdm_asyncio.gather(*tasks)
    del researcher
    return results


def batch_evaluate(input_path, output_path, config_path, batch_size=100):
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    if "langsmith" in config:
        for k, v in config["langsmith"].items():
            os.environ[k] = v

    df = pd.read_csv(input_path)
    # df = df.iloc[:batch_size, :]
    print(f"🚀 Starting batch evaluation on {len(df)} questions...")

    for i in range(0, len(df), batch_size):
        batch_df = df.iloc[i:i+batch_size, :]
        batch_questions = batch_df['question'].tolist()
        print(f"- Processing batch {i//batch_size + 1}: Questions {i+1} to {i+len(batch_questions)}")
        batch_results = asyncio.run(process_batch_async(config, batch_questions))
        batch_df = process_results(batch_df, batch_results, config["query_type"])
        batch_output_path = output_path.replace(".csv", f"_{i}-{i+len(batch_df)}.csv")
        batch_df.to_csv(batch_output_path, index=False)
        print(f"  ✅ Saved batch results to {batch_output_path}")


def main(input_path, output_path, config_path, only_eval):
    if only_eval:
        print("📊 Evaluation only mode - loading existing results")
        df = pd.read_csv(output_path)
    else:
        df = batch_evaluate(input_path, output_path, config_path)

    print("------ All Done ------")



if __name__ == "__main__":
    args = parse_args()
    main(**vars(args))
