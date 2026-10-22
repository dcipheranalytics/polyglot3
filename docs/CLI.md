# Command Line Interface

polyglot3 installs the `polyglot3` command (the original polyglot's
`polyglot` command, renamed):

```console
$ polyglot3 --help
usage: polyglot3 [-h] [--lang LANG] [--delimiter DELIMITER]
                 [--workers WORKERS] [-l LOG] [--debug]
                 {detect,tokenize,download,count,cat,ner,pos,sentiment} ...

options:
  -h, --help            show this help message and exit
  --lang LANG           Language to be processed
  --delimiter DELIMITER
                        Delimiter that seperates documents, records or even
                        sentences.
  --workers WORKERS     Number of parallel processes.
  -l, --log LOG         log verbosity level
  --debug               drop a debugger if an exception is raised.

tools:
  multilingual tools for all languages

  {detect,tokenize,download,count,cat,ner,pos,sentiment}
    detect              Detect the language(s) used in text.
    tokenize            Tokenize text into sentences and words.
    download            Download polyglot resources and models.
    count               Count words frequency in a corpus.
    cat                 Print the contents of the input file to the screen.
    ner                 Named entity recognition chunking.
    pos                 Part of Speech tagger.
    sentiment           Classify text to positive and negative polarity.
```

## Language

`ner`, `pos` and `sentiment` need to know the language of the input. Pass it
with `--lang`. Without it, polyglot3 detects the language from the first 4 KB
of the input and logs what it found.

## Input

Every subcommand except `download` reads standard input by default, or the
files given with `--input` (several files are processed in order). Input is
processed line by line; `--delimiter` changes the record separator.

## Tokenization

```console
$ echo "Bugün hava çok güzel. Yarın İstanbul'a gidiyorum." | polyglot3 --lang tr tokenize
Bugün hava çok güzel .
Yarın İstanbul'a gidiyorum .
```

Output has one sentence per line with tokens separated by spaces; see
[Tokenization](Tokenization.md) for `--only-word` and `--only-sent`.

## Tagging

`ner`, `pos` and `sentiment` split each line on whitespace, so pipe raw text
through `tokenize` first to separate punctuation:

```console
$ echo "Ankara Türkiye'nin başkentidir." | polyglot3 --lang tr tokenize | polyglot3 --lang tr ner
Ankara          I-LOC
Türkiye'nin     O
başkentidir     O
.               O

$ echo "harika ama berbat" | polyglot3 --lang tr sentiment
harika           1
ama             -1
berbat          -1
```

## Word counts

```console
$ cat news.txt
Ankara Türkiye'nin başkentidir. Ankara 1923'ten beri başkenttir.
İstanbul Türkiye'nin en kalabalık şehridir. İstanbul ve Ankara büyük şehirlerdir.

$ polyglot3 count --input news.txt --min-count 2
Ankara	3
Türkiye'nin	2
İstanbul	2
```

`count` also splits on whitespace, so "başkentidir." and "başkentidir" would
be different words. Tokenize first to count punctuation separately:

```console
$ polyglot3 --lang tr tokenize --input news.txt | polyglot3 count --min-count 2
.	4
Ankara	3
Türkiye'nin	2
İstanbul	2
```

`--most-freq K` keeps the K most frequent words instead. For many large
files, `--workers N` counts in N processes.

## Other subcommands

- `polyglot3 detect`: language of each line, see [Language Detection](Detection.md).
- `polyglot3 download`: install models, see [Downloading Models](Download.md).
- `polyglot3 cat`: print the input (useful with `--delimiter`).

## Debugging

`--log debug` prints more information and `--debug` starts a debugger when an
exception is raised.
