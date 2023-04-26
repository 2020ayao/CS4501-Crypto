# Submission information for the dApp Introduction HW
# https://aaronbloomfield.github.io/ccc/hws/dappintro/

# The filename of this file must be 'dappintro.py', else the submission
# verification routines will not work properly.

# You are welcome to have additional variables or fields in this file; you
# just can't remove variables or fields.


# Who are you?  Name and UVA userid.  The name can be in any human-readable format.
userid = "aly3ye"
name = "Adam Yao"


# eth.coinbase: this is the account that you deployed the smart contracts
# (and performed any necessary transactions) for this assignment.  Be sure to
# include the leading '0x' in the address.
eth_coinbase = "0x703ac4796189a1ce4ace3b3b10b62fcdc796fdb7"


# This dictionary contains the contract addresses of the various contracts
# that need to be deployed for this assignment.  The addresses do not need to
# be in checksummed form.  The contracts do, however, need to be deployed by
# the eth_coinbase address, above.  Be sure to include the leading '0x' in
# the address.
contracts = {

	# Your deployed Polls contract.  All of the action below on your Polls
	# contract is assumed to be with this one. The address does not need to
	# be in checksummed form.  It must have been deployed by the eth_coinbase
	# address, above.
	# 'poll': '0x7EF2e0048f5bAeDe046f6BF797943daF4ED8CB47',
	'poll': '0x3b87032eEA16a9B39eE4Af2973069164865F741B'

}


# This dictionary contains various information that will vary depending on the
# assignment.
other = {
	
	# This is the transaction hash where you voted on your own deployed
	# Polls contract in part 3 (deployment) of the assignment.
	'txn_hash_vote_yours': "0x49e367e51c2615157d704ec5730c57b33aacce7e619151c261c60db26bd1358d",

	# This is the transaction hash where you voted on the course Polls
	# contract in part 5 (vote) of the assignment.
	'txn_hash_vote_course': "0x1f61493bbc6f4f60e21898e3fecdfd7bbccc3a3f56cf4dcbe8c657e602beb44f",

	# Are you using the Desktop version of Remix?  If so, then True.  If you
	# are using the web version at https://remix.ethereum.org, then False.
	# This is just so we can see how many students are using each one.  If
	# you used both, choose this optoin based on which one you expect to use
	# more often in the future.
	'using_desktop_remix': True,

	# What was the purpose of your poll?  You should just copy-and-paste the
	# (string) value of the `purpose` variable from your Poll.sol here.
	'poll_purpose': "Vote on your favorite animal",

}


# These are various sanity checks, and are meant to help you ensure that you
# submitted everything that you are supposed to submit.  Other than
# submitting the necessary files to Gradescope, all other submission
# requirements are listed herein.  These values need to be changed to True
# (instead of False).
sanity_checks = {
	
	# Did you change the various choices in the `addChoice()` calls in the
	# constructor?  This is from the 'code base' section of the assignment.
	'make_changes_to_addchoice': True,

	# Did you change the value of the `purpose` variable in the code?  This
	# is from the 'code base' section of the assignment.
	'make_changes_to_purpose': True,

	# Did you try out the unit testing section of the homework?  This is from
	# part 2 (testing) of the assignment.
	'tried_out_unit_testing': True,

	# Did you deploy your Polls contract?  This is from part 3
	# (deployment) of the assignment.
	'deployed_choices_contract': True,

	# Did you vote on your own Polls contract?  This is from part 3
	# (deployment) of the assignment.
	'voted_on_your_poll': True,

	# Did you view the web page that reads from a Polls contract?  This is
	# from part 4 (web interface) of the assignment.
	'explored_web_interface': True,

	# Did you vote on the course-wide Polls contract?  This is from part 5
	# (vote) of the assignment.
	'voted_on_course_poll': True,

}


# While some of these are optional, you still have to replace those optional
# ones with the empty string (instead of None).
comments = {

	# How long did this assignment take, in hours?  Please format as an
	# integer or float.
	'time_taken': 2,

	# Any suggestions for how to improve this assignment?  This part is
	# completely optional.  If none, then you can have the value here be the
	# empty string (but not None).
	'suggestions': "",

	# Any other comments or feedback?  This part is completely optional. If
	# none, then you can have the value here be the empty string (but not
	# None).
	'comments': "",
}
