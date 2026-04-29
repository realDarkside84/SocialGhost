import psutil
import sys
import time
import click
import os
from perm_classes import *
from utils import *

class SocialGhost:
    def __init__(self, level=0, pwd_min=8, pwd_max=12, num_range=0,
                 leeter=False, years=0, chars=True, verbose=True, export='passwords.txt'):
        self.shit_level = level
        self.verbose_mode = verbose
        self.names = names_perm
        self.dates = dates_perm
        self.phones = phones_perm
        self.old_passwords = oldpwds
        self.total_result = []
        self.minimum_length = pwd_min
        self.maximum_length = pwd_max
        self.number_range = f"{num_range}" if num_range != 0 else "DISABLED"
        self.years_range = f"{years}-{time.localtime().tm_year + 1}" if years != 0 else "DISABLED"
        if chars:
            self.special_chars = "FULL SET" if self.shit_level >= 3 else "COMMON SET"
        else:
            self.special_chars = "DISABLED"
        self.leeting = "ENABLED" if leeter else "DISABLED"
        self.recipes = [[]]
        if num_range != 0:
            self.recipes.append(data_plus.nums_range(num_range))
        if years != 0:
            self.recipes.append(data_plus.years(years))
        if chars:
            if self.shit_level >= 3:
                self.recipes.append(data_plus.chars)
            else:
                self.recipes.append(("_", ".", "-", "!", "@", "*", "$", "?", "&", "%"))
        self.add_leet_perms = leeter
        self.export_file = export

    def __input(self, prompt):
        result = []
        while True:
            print(f"{G}[>] {prompt}{reset}", end="")
            data = input()
            if data:
                if " " in data.strip():
                    data = data.split(" ")
                else:
                    data = [data]
                for part in data:
                    for smaller_part in part.split(","):
                        if smaller_part:
                            result.append(smaller_part.strip())
            return result

    def __pwd_check(self, pwd):
        if (len(pwd) >= self.minimum_length) and (len(pwd) <= self.maximum_length) and (pwd not in self.total_result):
            return True
        return False

    def __simple_perm(self, target, *groups):
        for pair in zip(*groups, fillvalue=""):
            for targeted in target:
                pair = (targeted,) + pair
                for addition in self.recipes:
                    yield ("".join(pair + (added,)) for added in addition)

    def __commonPerms(self):
        for name in self.names.words:
            if self.__pwd_check(name):
                self.total_result.append(name)
        for date in self.dates.joined_dates:
            if self.__pwd_check(date):
                self.total_result.append(date)
            for thing in [self.names.words, self.names.one, self.names.two]:
                for justone in thing:
                    if self.__pwd_check(justone + date):
                        self.total_result.append(justone + date)
        for national_number in self.phones.national:
            if self.__pwd_check(national_number):
                self.total_result.append(national_number)
            for thing in [self.names.words, self.names.one, self.names.two]:
                for justone in thing:
                    if self.__pwd_check(justone + national_number):
                        self.total_result.append(justone + national_number)

    def __perm(self, target, *groups, perm_length=None):
        if groups:
            perm_length = perm_length if perm_length else len(groups) + 1
            if self.shit_level >= 5:
                for pair in ((target, pair2) for pair2 in groups):
                    for addition in self.recipes:
                        iterator = chain.from_iterable(pair + (addition,))
                        yield ("".join(p) for p in perm(iterator, perm_length) if
                               (self.__pwd_check("".join(p)) and not ("".join(p)).isdecimal()))
            else:
                for targeted in target:
                    for pair in (((targeted,) + pairs) for pairs in zip(*groups, fillvalue="")):
                        for addition in self.recipes:
                            if not addition:
                                yield ("".join(p) for p in perm(pair, perm_length) if
                                       (self.__pwd_check("".join(p)) and not ("".join(p)).isdecimal()))
                            else:
                                for added in addition:
                                    iterator = pair + (added,)
                                    yield ("".join(p) for p in perm(iterator, perm_length) if
                                           (self.__pwd_check("".join(p)) and not ("".join(p)).isdecimal()))

    def __perms(self, *main_group, others, perm_length=None):
        iters = []
        for other_group in others:
            iters.append(self.__perm(*main_group, other_group, perm_length=perm_length))
        iters.append(self.__perm(*main_group, *others, perm_length=perm_length))
        return chain.from_iterable(iters)

    def __export(self):
        if self.total_result:
            sys.stdout.write(f"{B}[+] Payload written to disk\r{reset}")
            sys.stdout.flush()
            with open(self.export_file, 'w') as f:
                for pwd in self.total_result:
                    f.write(f"{pwd}\n")
            print(f"{G}[+] Payload written to disk: {self.export_file}{reset}")

    def perms_generator(self):
        self.__commonPerms()
        mixes = [
            self.__simple_perm(self.names.words, ),
            self.__perms(self.names.words, others=(self.dates.days, self.dates.months, self.dates.years), ),
            self.__perm(self.names.one, self.dates.joined_dates, ),
            self.__perm(self.names.two, self.dates.joined_dates, ),
            self.__perms(self.names.words,
                         others=(self.phones.national, self.phones.first_four, self.phones.last_four), ),
            self.__perm(self.names.one, self.phones.national, ),
            self.__perm(self.names.two, self.phones.national, ),
            self.__perms(self.names.one, others=(self.phones.first_four, self.phones.last_four), ),
            self.__perms(self.names.two, others=(self.phones.first_four, self.phones.last_four), ),
            self.__perm(self.names.words, self.dates.years, self.phones.first_four, ),
            self.__perm(self.names.words, self.dates.years, self.phones.last_four, ),
            self.__perm(self.names.words, self.dates.years, self.phones.national, )]
        if self.old_passwords.passwords:
            for pwd in self.old_passwords.passwords:
                for iterator in (data_plus.nums_range(100), data_plus.years(1900), data_plus.chars,):
                    mixes.append(
                        ("".join(p) for one in iterator for p in perm((pwd, one), 2) if self.__pwd_check("".join(p))))
            mixes.append(self.__perm(self.old_passwords.passwords, self.names.words, ))
            mixes.append(self.__perms(self.old_passwords.passwords,
                                      others=(self.dates.days, self.dates.months, self.dates.years), ))
            mixes.append(self.__perms(self.old_passwords.passwords,
                                      others=(self.phones.national, self.phones.first_four, self.phones.last_four), ))
        if self.shit_level >= 4:
            mixes.append(self.__perm(self.names.words, self.dates.days, self.dates.months, self.dates.years))
            mixes.append(self.__perm(self.names.one, self.names.two, self.dates.joined_dates))
            mixes.append(self.__perm(self.names.words, self.phones.first_four, self.phones.last_four))
            mixes.append(self.__perm(self.names.one, self.names.two, self.phones.national))
            mixes.append(self.__perm(self.names.one, self.names.two, self.phones.first_four, self.phones.last_four, ))
            mixes.append(
                self.__perm(self.names.words, self.dates.years, self.phones.first_four, self.phones.last_four, ))
            mixes.append(self.__perm(self.names.words, self.dates.days, self.dates.months, self.phones.national, ))
            mixes.append(self.__perm(self.dates.days, self.dates.months, self.dates.years, ))
            mixes.append(self.__perm(self.phones.national, self.dates.years, ))
            mixes.append(self.__perm(self.phones.first_four, self.phones.last_four, self.dates.years, ))
        
        sys.stdout.write(f"{B}[+] Synthesizing credential patterns...{reset}\r")
        sys.stdout.flush()
        for generator in chain.from_iterable(mixes):
            for pwd in generator:
                if self.__pwd_check(pwd):
                    self.total_result.append(pwd)
                    if self.verbose_mode:
                        sys.stdout.write(f"{B}[+] Synthesizing: {pwd : <25} [N:{len(self.total_result) :_<10}]{reset}\r")
                        sys.stdout.flush()

        self.__export()
        if self.add_leet_perms:
            print(f"{B}[+] Applying leet transformations...{reset}")
            leeted_results = []
            with open(self.export_file, 'r') as data:
                for pwd in data:
                    leeted_results.extend(data_plus.leet_perm(pwd.strip()))
            
            self.total_result = leeted_results
            self.export_file = "Leeted-"+self.export_file
            self.__export()

    def __print_banner(self):
        banner = f"""{R}
 ███████╗ ██████╗  ██████╗██╗ █████╗ ██╗      ██████╗ ██╗  ██╗ ██████╗ ███████╗████████╗
 ██╔════╝██╔═══██╗██╔════╝██║██╔══██╗██║     ██╔════╝ ██║  ██║██╔═══██╗██╔════╝╚══██╔══╝
 ███████╗██║   ██║██║     ██║███████║██║     ██║  ███╗███████║██║   ██║███████╗   ██║   
 ╚════██║██║   ██║██║     ██║██╔══██║██║     ██║   ██║██╔══██║██║   ██║╚════██║   ██║   
 ███████║╚██████╔╝╚██████╗██║██║  ██║███████╗╚██████╔╝██║  ██║╚██████╔╝███████║   ██║   
 ╚══════╝ ╚═════╝  ╚═════╝╚═╝╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝   ╚═╝   
               [ // SocialGhost // Credential Synthesis Engine ]
               [ // Author: realDarkside84 // Version: 1.0 // ]
{reset}
{W} +-----------------------------------------------------------------------+
 |                      [ // PROFILE SYNTHESIS ENGINE // ]               |
 +-----------------------------------------------------------------------+
 | > Numeric Mutation Range    : [{self.number_range : <39}] |
 | > Year Injection Range      : [{self.years_range : <39}] |
 | > Symbol Injection Layer    : [{self.special_chars : <39}] |
 | > Leet Transformation       : [{self.leeting : <39}] |
 | > Output Stream Mode        : [{"VERBOSE" if self.verbose_mode else "SILENT" : <39}] |
 | > Export Target             : [{self.export_file : <39}] |
 +-----------------------------------------------------------------------+
 +-----------------------------------------------------------------------+
 |                      [ // CREDENTIAL MATRIX // ]                      |
 +-----------------------------------------------------------------------+
 | > Min Length                : [{self.minimum_length : <39}] |
 | > Max Length                : [{self.maximum_length : <39}] |
 | > Complexity Level          : [{ {0: "SIMPLE", 1: "AVERAGE", 2: "CYBER AWARE", 3: "PARANOID", 4: "NERD", 5: "NUCLEAR"}[self.shit_level] : <39}] |
 +-----------------------------------------------------------------------+
 HELP: Use commas to separate multiple entries. Do not use spaces.{reset}"""
        print(banner)

    def interface(self):
        self.__print_banner()
        self.names = self.names(self.__input("Primary Names (Target, family, or pets): "),
                                complicated=self.shit_level)
        self.names.add_keywords(
            self.__input("Target Keywords (Nicknames, jobs, hobbies): "))
        self.dates = self.dates(
            self.__input("Important Dates (Format: [DD-MM-YYYY]): "),
            complicated=self.shit_level)
        self.phones = self.phones(
            self.__input("Contact Numbers (Format: +[CountryCode][Number]): "))
        self.old_passwords = self.old_passwords(
            self.__input("Known Patterns (Old passwords or common phrases): "),
            complicated=self.shit_level)
        
        start_time = time.time()
        try:
            print(f"{B}[+] Synthesis initialized...{reset}")
            self.perms_generator()
        except KeyboardInterrupt:
            print(f'\n{R}[!] Interrupted by operator. Exiting...{reset}')
            self.__export()
        finally:
            process = psutil.Process(os.getpid())
            elapsed = round(time.time()-start_time, 2)
            
            summary = f"""
{W} +-----------------------------------------------------------------------+
 |                      [ // EXECUTION SUMMARY // ]                      |
 +-----------------------------------------------------------------------+
 | > Generated Credentials     : [{len(self.total_result) : <39}] |
 | > Execution Time            : [{str(elapsed)+'s' : <39}] |
 | > Memory Footprint          : [{str(round(process.memory_info().rss / 1024 ** 2, 2))+'MB RSS / '+str(round(process.memory_info().vms / 1024 ** 2, 2))+'MB VMS' : <39}] |
 +-----------------------------------------------------------------------+
{G}[✓] Process completed{reset}
"""
            print(summary)
            sys.exit(0)

@click.command()
@click.option('-l', '--level', metavar='', type=click.Choice(['0', '1', '2', '3', '4', '5']), default='0', help='Level of complication.')
@click.option('--min', 'pmin', metavar='', type=int, default=8, help='Minimum length.')
@click.option('--max', 'pmax', metavar='', type=int, default=12, help='Maximum length.')
@click.option('-r', '--num-range', metavar='', type=int, default=0, help='Numeric range.')
@click.option('--leet', metavar='', is_flag=True, default=False, help='Leet permutations.')
@click.option('-y', '--years', metavar='', type=int, default=0, help='Year range.')
@click.option('-c', '--chars', metavar='', is_flag=True, default=False, help='Special characters.')
@click.option('-v', '--verbose', metavar='', is_flag=True, default=False, help='Verbose mode.')
@click.option('-x', '--export', metavar='', type=str, default='passwords.txt', help='Export file.')
def main(level, pmin, pmax, num_range, leet, years, chars, verbose, export):
    gen = SocialGhost(int(level), pmin, pmax, num_range, leet, years, chars, verbose, export)
    gen.interface()

if __name__ == '__main__':
    main()

