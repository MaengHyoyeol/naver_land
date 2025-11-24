#!/usr/bin/env python3
"""
동일 매물 그룹 내 공인중개사무소 순위를 조회하는 CLI 도구
"""

import argparse
import sys
from pathlib import Path

import pandas as pd

from src.data_parser import DataParser


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="동일 매물 내 공인중개사무소 순위를 계산합니다."
    )
    parser.add_argument(
        "--agent",
        "-a",
        help="관심 공인중개사무소 이름 (부분 문자열 허용)",
    )
    parser.add_argument(
        "--parsed-csv",
        "-p",
        help="이미 파싱된 CSV 경로 (예: data/영등포아트자이_파싱완료.csv)",
    )
    parser.add_argument(
        "--raw-csv",
        "-r",
        help="원본 매물 CSV 경로 (예: data/영등포_아트자이_매물_*.csv)",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="결과를 저장할 CSV 경로 (지정하지 않으면 터미널에 출력)",
    )
    return parser.parse_args()


def load_dataframe(parsed_csv: str, raw_csv: str) -> pd.DataFrame:
    if parsed_csv:
        csv_path = Path(parsed_csv)
        if not csv_path.exists():
            raise FileNotFoundError(f"파싱 CSV를 찾을 수 없습니다: {parsed_csv}")
        return pd.read_csv(csv_path)
    
    if raw_csv:
        csv_path = Path(raw_csv)
        if not csv_path.exists():
            raise FileNotFoundError(f"원본 CSV를 찾을 수 없습니다: {raw_csv}")
        raw_df = pd.read_csv(csv_path)
        parser = DataParser()
        return parser.parse_dataframe(raw_df)
    
    raise ValueError("parsed-csv 또는 raw-csv 중 하나는 반드시 지정해야 합니다.")


def main() -> None:
    args = parse_arguments()
    
    try:
        df = load_dataframe(args.parsed_csv, args.raw_csv)
    except Exception as exc:
        print(f"[오류] 데이터를 불러오지 못했습니다: {exc}", file=sys.stderr)
        sys.exit(1)
    
    agent_name = args.agent
    if not agent_name:
        agent_name = input("내 공인중개사무소 이름을 입력하세요: ").strip()
    
    rankings = DataParser.calculate_agent_rankings(df, agent_name)
    
    if rankings.empty:
        print("⚠️ 지정한 공인중개사무소에 해당하는 순위 데이터를 찾을 수 없습니다.")
        sys.exit(0)
    
    if args.output:
        output_path = Path(args.output)
        rankings.to_csv(output_path, index=False, encoding="utf-8-sig")
        print(f"✅ 결과를 저장했습니다: {output_path}")
    else:
        pd.set_option("display.max_rows", None)
        pd.set_option("display.width", 0)
        print("✅ 동일 매물 내 순위 결과")
        print(rankings)


if __name__ == "__main__":
    main()

