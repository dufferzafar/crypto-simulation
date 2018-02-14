default: run

OUT_DIR = output

run:
	@python3 run.py 10 0.3 3 10

large:
	@python3 run.py -q --until 5000 10 0.3 3 10

clean:
	@printf "\n >>>> Cleaning graphs directory "
	@rm -rf $(OUT_DIR)/*.*
