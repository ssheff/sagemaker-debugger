# Standard Library
import os
import uuid

# Third Party
import numpy as np
import pytest

# First Party
from smdebug.core.collection_manager import CollectionManager
from smdebug.core.config_constants import DEFAULT_COLLECTIONS_FILE_NAME
from smdebug.core.writer import FileWriter
from smdebug.exceptions import RuleEvaluationConditionMet
from smdebug.rules.generic import Confusion
from smdebug.rules.rule_invoker import invoke_rule
from smdebug.trials import create_trial


def gen_y_and_y_hat(path, trial, step, y, y_name, y_hat, y_hat_name, colls={}):
    trial_dir = os.path.join(path, trial)
    with FileWriter(trial_dir=trial_dir, step=step, worker="algo-1") as fw:
        fw.write_tensor(tdata=y, tname=y_name)
        fw.write_tensor(tdata=y_hat, tname=y_hat_name)
    c = CollectionManager()
    for coll in colls:
        c.add(coll)
        c.get(coll).tensor_names = colls[coll]
    c.export(trial_dir, DEFAULT_COLLECTIONS_FILE_NAME)


@pytest.mark.slow  # 0:06 to run
def test_confusion():
    base_path = "ts_output1/rule_invoker/"
    path = base_path
    cat_no = 10

    # Test 1: identity matrix, rule should not fire
    run_id = str(uuid.uuid4())
    y = np.random.randint(cat_no, size=(100,))
    y_hat = y
    gen_y_and_y_hat(
        path, run_id, 0, y, "y", y_hat, "y_hat", colls={"labels": ["y"], "preds": ["y_hat"]}
    )
    tr = create_trial(os.path.join(path, run_id))
    r = Confusion(tr, labels_collection="labels", predictions_collection="preds")
    invoke_rule(r, start_step=0, end_step=1, raise_eval_cond=True)

    # Test 2: should fail on row 4 because the
    run_id = str(uuid.uuid4())
    y = np.arange(cat_no)
    y_hat = np.copy(y)
    y_hat[4] = 7
    gen_y_and_y_hat(path, run_id, 1, y, "foo", y_hat, "bar")
    tr = create_trial(os.path.join(path, run_id))
    r = Confusion(tr, cat_no, "foo", "bar")
    try:
        invoke_rule(r, start_step=1, end_step=2, raise_eval_cond=True)
        assert False
    except RuleEvaluationConditionMet:
        pass

    # Test 3: should fail on row 4, just for one condition
    r = Confusion(tr, cat_no, "foo", "bar", min_diag=0.0, max_off_diag=0.01)
    try:
        invoke_rule(r, start_step=1, end_step=2, raise_eval_cond=True)
        assert False
    except RuleEvaluationConditionMet:
        pass

    # Test 4: no arguments, all defaults
    run_id = str(uuid.uuid4())
    y = np.arange(10)
    y_hat = y
    # 'label' and 'pred' are magic names
    gen_y_and_y_hat(path, run_id, 1, y, "labels", y_hat, "predictions")
    tr = create_trial(os.path.join(path, run_id))
    r = Confusion(tr)
    invoke_rule(r, start_step=1, end_step=2, raise_eval_cond=True)
