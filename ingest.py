# ingest.py
import argparse
from rag_engine import Ingestor


def main(docs_folder='docs', persist_dir='chroma_db'):
    ing = Ingestor(docs_folder=docs_folder, persist_dir=persist_dir)
    ing.ingest_all()
    print('Ingestion complete.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--docs_folder', default='docs')
    parser.add_argument('--persist_dir', default='chroma_db')
    args = parser.parse_args()
    main(args.docs_folder, args.persist_dir)
