import argparse
import lib.ssDiagnostics as diags

def process_command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--game",
                        dest="game",
                        help="Which game to start in (e.g. 'metroid3')",
                        metavar="<game_name>",
                        default='zelda3')
    parser.add_argument("--diagnostics",
                        dest="diagnostics",
                        help="Run Diagnostics",
                        metavar="<diagnostics>",
                        default='')

    command_line_args = vars(parser.parse_args())
    return command_line_args

def main():
    command_line_args = process_command_line_args()

    if command_line_args["diagnostics"] != "":
        print("\n".join(diags.output()))

if __name__ == "__main__":
    main()
