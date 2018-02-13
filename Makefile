default: run graphs

OUT_DIR = output

run:
	@printf "\n --- Starting simulation --- \n\n"
	@python3 run.py

graphs:
	@printf "\n --- Converting graphs to images --- \n"
	@python3 graphs.py

clean:
	@printf "\n --- Cleaning output directory --- \n"
	@rm -rf $(OUT_DIR)/*.*

