======================================================
Vitrage Machine Learning plugins - Jaccard Correlation
======================================================

Overview
========

Machine Learning algorithms can contribute to Vitrages' purposes. The `Jaccard
Correlation <http://en.wikipedia.org/wiki/Jaccard_index>`_
plugin was created in order to calculate correlations between
alarms, to recommend the client on new templates for better predicting alarms
and better RCA in the future.

This document describes the usage of the Machine Learning service plugin -
Jaccard Correlation.

Machine Learning service configuration
--------------------------------------
In ``/etc/vitrage/vitrage.conf``:

Activate the plugins to be used:

[machine_learning]

plugins = jaccard_correlation

**   In order to use different plugin, insert plugin names separated by commas.


Jaccard Correlation plugin configuration
----------------------------------------

1. This plugin calculates correlations for each pair of alarms, while an alarm
defined as (alarm name, resource type).

   The output is a report, generated once in 'num_of_events_to_flush', with
   correlation score for each pair of alarms, sorted by correlation score.
   For now, the report only shows correlations but not causality.

2. In ``/etc/vitrage/vitrage.conf``:

   Configure Jaccard Correlations plugin:

   [jaccard_correlation]

   num_of_events_to_flush = ``<number of events to catch before flushing
   saved data, by default 1000>``

   output_folder = ``<the folder to which reports will be saved, by default /tmp>``

   correlation_threshold = ``<all alarms pairs with correlation score above
   threshold will appear in the report, the default is 0>``

   high_corr_score = ``<high correlation threshold, by default 0.9>``

   med_corr_score = ``<medium correlation score threshold, 0.5 by default>``
