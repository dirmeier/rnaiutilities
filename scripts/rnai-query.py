# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 26.06.17


if __name__ == "__main__":
    q = Query()
    res = q.query(library="d",
                 featureclass="cells",
                  gene="star", sample=10)
    res.dump("/Users/simondi/Desktop/simon.tsv")
