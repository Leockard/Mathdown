# runtests.py
# runs mathdown on every file in this dir and compares it to the desired output


if __name__ == "__main__":
    import os
    import re
    from subprocess import call

    # test every .Mmd in this directory
    tests = [fl for fl in os.listdir(os.getcwd()) if re.match(".*\.Mmd", fl)]

    for test in tests:
        # run test
        print("Testing " + test + "...")
        retcode = call(["python3", "../src/mathdown.py", test])
        
        if retcode:
            print("ERROR.")
            exit(1)

        # diff it to _target.md
        md_file = test.split(".")[0] + ".md"
        target = test.split(".")[0] + "_target.md"
        diff = call(["diff", md_file, target])
        print((not diff) and "Pass." or "FAIL.")

    
