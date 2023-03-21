// SPDX-License-Identifier: GPL-3.0-or-later

pragma solidity ^0.8.17;
import "./IGradebook.sol";

contract Gradebook is IGradebook{
    uint public override num_assignments;
    mapping (address => bool) public override tas;
    mapping (uint => mapping(string => uint) ) public override scores;
    mapping (uint => uint) public override max_scores;
    mapping (uint => string) public override assignment_names;
    address public override instructor;

    constructor() {
        instructor = msg.sender;

        // designateTA(0x0123456789abcDEF0123456789abCDef01234567);
        // addAssignment("HW1",10);
        // addAssignment("HW2",10);
        // addGrade("mst3k",0,5);
        // addGrade("mst3k",1,10);

        // addGrade("aly3ye",0,5);
        // addGrade("aly3ye",1,10);

    }

    //----------------------------- //

    function getAverage(string memory _student) public override view returns (uint) {
        uint points = 0;
        uint total = 0;
        uint index = 0;
        // uint assign_count = 0;
    
        while (index < num_assignments) {
            uint score = scores[index][_student];
            if (score > 0) {
                // assign_count += 1;
                total += max_scores[index];
                points += score;
            }
            index++;
        }
        return points * 10000 / total;

    }

    function designateTA (address _ta) public override{
        require(msg.sender == instructor, "only instructor can designate TAs");
        // require(!tas[_ta], "ta address already designated"); // but i think we can redesignate ??
        tas[_ta] = true;
    }

    

    function addGrade(string memory _student, uint _assignment, uint _score) public override {
        require(msg.sender == instructor || tas[msg.sender], "caller must be instructor or designated TA!");
        require(_assignment >= 0 && _assignment < num_assignments, "assignment ID must be valid");
        require(_score <= max_scores[_assignment], "score must be lower than or equal to max score");
        scores[_assignment][_student] = _score;
        emit gradeEntryEvent(_assignment);
        
    }

    function addAssignment(string memory _name, uint _max_score) public override returns (uint) {
        require(msg.sender == instructor || tas[msg.sender], "caller must be instructor or designated TA!");
        assignment_names[num_assignments] = _name;
        max_scores[num_assignments] = _max_score;
        emit assignmentCreationEvent(num_assignments);
        num_assignments++;
        return num_assignments;
    }

    function requestTAAccess() public override {
        tas[msg.sender] = true;
    }

    function supportsInterface(bytes4 interfaceId) external pure returns (bool) {
        return interfaceId == type(IGradebook).interfaceId || interfaceId == 0x01ffc9a7;
}
    
}
