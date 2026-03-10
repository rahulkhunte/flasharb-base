// SPDX-License-Identifier: MIT
pragma solidity ^0.8.10;

interface IPool {
    function flashLoanSimple(
        address receiverAddress, address asset,
        uint256 amount, bytes calldata params, uint16 referralCode
    ) external;
}

interface IERC20 {
    function approve(address spender, uint256 amount) external returns (bool);
    function transfer(address to, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
}

// Uniswap V3 style router
interface IUniRouter {
    struct ExactInputSingleParams {
        address tokenIn; address tokenOut; uint24 fee;
        address recipient; uint256 amountIn;
        uint256 amountOutMinimum; uint160 sqrtPriceLimitX96;
    }
    function exactInputSingle(ExactInputSingleParams calldata params)
        external payable returns (uint256 amountOut);
}

// Aerodrome style router (uses int24 tickSpacing, no fee param)
interface IAeroRouter {
    struct ExactInputSingleParams {
        address tokenIn; address tokenOut; int24 tickSpacing;
        address recipient; uint256 deadline; uint256 amountIn;
        uint256 amountOutMinimum; uint160 sqrtPriceLimitX96;
    }
    function exactInputSingle(ExactInputSingleParams calldata params)
        external payable returns (uint256 amountOut);
}

contract FlashArb {
    address public owner;
    IPool       public pool;
    IUniRouter  public uniRouter;
    IAeroRouter public aeroRouter;

    constructor(address _pool, address _uniRouter, address _aeroRouter) {
        owner       = msg.sender;
        pool        = IPool(_pool);
        uniRouter   = IUniRouter(_uniRouter);
        aeroRouter  = IAeroRouter(_aeroRouter);
    }

    // Called by Python — passes route info via params
    function executeArb(address token, uint256 amount, bytes calldata params) external {
        require(msg.sender == owner, "Not owner");
        pool.flashLoanSimple(address(this), token, amount, params, 0);
    }

    function executeOperation(
        address asset, uint256 amount, uint256 premium,
        address, bytes calldata params
    ) external returns (bool) {
        require(msg.sender == address(pool), "Caller not pool");
        uint256 debt = amount + premium;

        // Decode route: buyOnUni, midToken, uniFee, aeroTick
        (bool buyOnUni, address midToken, uint24 uniFee, int24 aeroTick) =
            abi.decode(params, (bool, address, uint24, int24));

        uint256 midOut;

        if (buyOnUni) {
            // Step 1: Buy midToken on Uniswap using WETH
            IERC20(asset).approve(address(uniRouter), amount);
            midOut = uniRouter.exactInputSingle(
                IUniRouter.ExactInputSingleParams({
                    tokenIn: asset, tokenOut: midToken, fee: uniFee,
                    recipient: address(this), amountIn: amount,
                    amountOutMinimum: 0, sqrtPriceLimitX96: 0
                })
            );
            // Step 2: Sell midToken on Aerodrome for WETH
            IERC20(midToken).approve(address(aeroRouter), midOut);
            aeroRouter.exactInputSingle(
                IAeroRouter.ExactInputSingleParams({
                    tokenIn: midToken, tokenOut: asset, tickSpacing: aeroTick,
                    recipient: address(this), deadline: block.timestamp,
                    amountIn: midOut, amountOutMinimum: debt, sqrtPriceLimitX96: 0
                })
            );
        } else {
            // Step 1: Buy midToken on Aerodrome using WETH
            IERC20(asset).approve(address(aeroRouter), amount);
            midOut = aeroRouter.exactInputSingle(
                IAeroRouter.ExactInputSingleParams({
                    tokenIn: asset, tokenOut: midToken, tickSpacing: aeroTick,
                    recipient: address(this), deadline: block.timestamp,
                    amountIn: amount, amountOutMinimum: 0, sqrtPriceLimitX96: 0
                })
            );
            // Step 2: Sell midToken on Uniswap for WETH
            IERC20(midToken).approve(address(uniRouter), midOut);
            uniRouter.exactInputSingle(
                IUniRouter.ExactInputSingleParams({
                    tokenIn: midToken, tokenOut: asset, fee: uniFee,
                    recipient: address(this), amountIn: midOut,
                    amountOutMinimum: debt, sqrtPriceLimitX96: 0
                })
            );
        }

        IERC20(asset).approve(address(pool), debt);
        return true;
    }

    function rescue(address token) external {
        require(msg.sender == owner, "Not owner");
        IERC20(token).transfer(owner, IERC20(token).balanceOf(address(this)));
    }

    receive() external payable {}
}
