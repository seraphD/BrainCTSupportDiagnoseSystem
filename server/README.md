Use

```
npm run app
```

to run this service.

## Brain structure identify

Because I didn't find any public precise way to identify brain structure while it's an essential step. So I figured out an approximate way. Simply speaking, comparing uploaded pictures
with a standard model. Assume there are 107 pictures in the model, and the system receive 27 pictures. Suppose the first 20 pictures in the model contain frontal lobe, so the sysytem
will seek frontal lobe in the first 20 * 27 / 107 pictures in uploaded pictures. After all structures are confirmed, the system will then find symmetry axis and use some predefined lines
to split areas and identtify corronsponding brain lobe.

## Symmetry axis finding

Also, I didn't find an existing algorithm to find a symmetry axis. So I implemented the simplest way, to try all possible degrees.

## Keras

A neural network is used in this system to classify pictures into two categories: normal and abnormal.

## Reference

If a CT picture is categoried as abnormal, then the system will identify brain structure and compare their pixel average with normal structures. If a structure has a lower or higher
average, the system will report it to front end.
