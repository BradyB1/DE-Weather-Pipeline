import sys
from extract_weather import run_extract
from load_postgres import run_load


def run_pipeline_step(step):
    if step =="extract":
        print("starting extract step...")
        run_extract()
        print("Extract step complete")
        
    elif step == "load":
        print("starting load step...")
        run_load()
        print("Load step complete...")
    
    else:
        print("Invalid step.")
        print("Use one of these: ")
        print(" python main.py extract")
        print(" python main.py load")

def main():
    if len(sys.argv) < 2:
        print("Choose a step to run:")
        print("  python main.py extract")
        print("  python main.py load")
        print("")
        print("Run transform separately in WSL:")
        print("  python transform_weather_spark.py")
        return

    step = sys.argv[1].lower()
    run_pipeline_step(step)


if __name__ == "__main__":
    main()